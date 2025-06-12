from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Produto, Pedido, ItemPedido
from django.contrib import messages
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from decimal import Decimal
import qrcode
import base64
import requests
from django.http import HttpResponse
import json



# View Home
def home(request):
    return render(request, 'cafeteria/home.html')

# Criação da View Produto ...:
@login_required
def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'cafeteria/cardapio.html', {'produtos': produtos})

# Criação de View Usuario Registro ...:
def registrar_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'cafeteria/registro.html', {'form': form})

# Adiciona o produto ao carrinho ...:
def adicionar_ao_carrinho(request, produto_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        produto = get_object_or_404(Produto, id=produto_id)
        carrinho = request.session.get('carrinho', {})
        quantidade = int(request.POST.get('quantidade', 1))

        carrinho[str(produto_id)] = carrinho.get(str(produto_id), 0) + quantidade
        request.session['carrinho'] = carrinho

        return JsonResponse({'mensagem': f"{quantidade}x {produto.nome} adicionado(s) ao carrinho!"})
    return JsonResponse({'erro': 'Requisição inválida'}, status=400)

# Verifica o carrinho ...:
def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    itens = []
    total = 0

    for produto_id, quantidade in carrinho.items():
        produto = Produto.objects.get(id=produto_id)
        subtotal = produto.preco * quantidade
        total += subtotal
        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

    return render(request, 'cafeteria/carrinho.html', {'itens': itens, 'total': total})

# Remove o produto do carrinho ...:
def remover_do_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    carrinho.pop(str(produto_id), None)
    request.session['carrinho'] = carrinho
    return redirect('ver_carrinho')

# Atualiza a quantidade do produto no carrinho ...:
def quantidade_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(carrinho.values())
    return JsonResponse({'total': total})




# Finaliza o pedido e integra com Asaas PIX
@login_required
def finalizar_pedido(request):
    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('lista_produtos')

    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo_entrega = request.POST.get('tipo_entrega')
        endereco = request.POST.get('endereco') if tipo_entrega == 'delivery' else 'Retirada no local'
        cpf = request.POST.get("cpf")

        total = Decimal('0.00')
        for produto_id, quantidade in carrinho.items():
            produto = Produto.objects.get(id=produto_id)
            subtotal = produto.preco * quantidade
            total += subtotal

        if tipo_entrega == 'delivery':
            total += Decimal('10.00')

        # Cria o pedido local (sem salvar ainda o asaas_id)
        pedido = Pedido.objects.create(nome=nome, endereco=endereco)

        for produto_id, quantidade in carrinho.items():
            produto = Produto.objects.get(id=produto_id)
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco=produto.preco
            )

        # Integração com Asaas
        headers = {
            "Content-Type": "application/json",
            "access_token": "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmE4MDdhNWJiLWM1ZTktNGFhZi04MzlkLTE1NDYwZjY5YjgwZjo6JGFhY2hfYTA2MjM5NmItNzUwMi00MTU0LWIyODQtZjE5YTI4NmZlMDRm"
        }

        cliente_data = {
            "name": nome,
            "email": request.user.email or "teste@cliente.com",
            "cpfCnpj": cpf,
        }

        cliente_resp = requests.post("https://sandbox.asaas.com/api/v3/customers", json=cliente_data, headers=headers)

        try:
            cliente_info = cliente_resp.json()
            cliente_id = cliente_info.get("id")
            if not cliente_id:
                raise ValueError("ID do cliente não retornado.")
        except Exception as e:
            print("Erro ao criar cliente no Asaas:", cliente_resp.text)
            messages.error(request, "Erro ao processar cliente no Asaas. Tente novamente.")
            return redirect("ver_carrinho")

        cobranca_data = {
            "customer": cliente_id,
            "billingType": "PIX",
            "value": float(total),
            "dueDate": str(date.today()),
            "pixKey": "2d29e475-cc76-44eb-a58c-4ec715a401e6"
        }

        cobranca_resp = requests.post("https://sandbox.asaas.com/api/v3/payments", json=cobranca_data, headers=headers)

        try:
            pagamento = cobranca_resp.json()
            payment_id = pagamento.get("id")
            pix_copia_cola = pagamento.get("pixCopyPaste") or pagamento.get("invoiceUrl")

            # Salva o asaas_id no pedido
            pedido.asaas_id = payment_id
            pedido.save()

            # Gera o QR Code em base64
            qr_image = qrcode.make(pix_copia_cola)
            buffer = BytesIO()
            qr_image.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        except ValueError:
            messages.error(request, "Erro inesperado ao processar o pagamento.")
            return redirect("ver_carrinho")

        # Limpa o carrinho após gerar cobrança
        request.session['carrinho'] = {}

        return render(request, 'cafeteria/pagamento_pix.html', {
            'pix_qr_code': qr_code_base64,
            'pix_copia_cola': pix_copia_cola,
            'pedido_id': pedido.id
        })

    # Se for GET
    itens = []
    total = Decimal('0.00')
    for produto_id, quantidade in carrinho.items():
        produto = Produto.objects.get(id=produto_id)
        subtotal = produto.preco * quantidade
        total += subtotal
        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

    total_com_taxa = total + Decimal('10.00') if request.GET.get('tipo_entrega') == 'delivery' else total

    return render(request, 'cafeteria/finalizar.html', {
        'itens': itens,
        'total': total,
        'total_com_taxa': total_com_taxa,
        'tipo_entrega': request.GET.get('tipo_entrega', 'retirada')
    })
















@login_required
def verificar_status_pagamento(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        return JsonResponse({'pago': pedido.pago})
    except Pedido.DoesNotExist:
        return JsonResponse({'pago': False})



# Webhook para receber notificações do Asaas ...:
@csrf_exempt
def asaas_webhook(request):
    if request.method == "POST":
        payload = json.loads(request.body)

        if payload.get("event") == "PAYMENT_RECEIVED":
            payment_id = payload.get("payment", {}).get("id")

            # encontre o pedido com base no ID externo (por ex, invoiceNumber, ou salve o ID no pedido)
            try:
                pedido = Pedido.objects.get(asaas_id=payment_id)  # Ex: você salvou esse ID no pedido
                pedido.pago = True
                pedido.save()
                print(f"✅ Pagamento confirmado para o pedido #{pedido.id}")
            except Pedido.DoesNotExist:
                print("❌ Pedido não encontrado para o pagamento:", payment_id)

        return JsonResponse({"status": "ok"})

    return HttpResponse("Webhook OK")

def pagamento_sucesso(request):
    return render(request, 'cafeteria/pagamento_sucesso.html')