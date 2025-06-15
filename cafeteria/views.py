from .models import Produto, Pedido, ItemPedido
from .forms import RegistroForm
from .models import Perfil
from django.shortcuts import render, redirect , get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from io import BytesIO
from decimal import Decimal
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import qrcode
import base64
import requests
import threading
import json
import time
from datetime import datetime





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
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Cria o perfil com os dados extras
            Perfil.objects.create(
                user=user,
                nome=form.cleaned_data['nome'],
                cpf=form.cleaned_data['cpf'],
                data_nascimento=form.cleaned_data['data_nascimento'],
                celular=form.cleaned_data['celular']
            )

            login(request, user)
            return redirect('/')
    else:
        form = RegistroForm()
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


@require_POST
def alterar_quantidade(request, produto_id):
    try:
        nova_quantidade = int(request.POST.get('quantidade'))
        if nova_quantidade < 1:
            return redirect('remover_do_carrinho', produto_id=produto_id)

        carrinho = request.session.get('carrinho', {})
        carrinho[str(produto_id)] = nova_quantidade
        request.session['carrinho'] = carrinho
        return redirect('ver_carrinho')

    except (ValueError, TypeError):
        return HttpResponseBadRequest("Quantidade inválida")




def enviar_email_confirmacao(pedido, user_email):
    assunto = f"Pedido #{pedido.id} confirmado - The Best Coffee"
    contexto = {
        'pedido': pedido,
        'itens': pedido.itens.all(),
    }

    html_conteudo = render_to_string('cafeteria/email_confirmacao.html', contexto)
    texto_conteudo = strip_tags(html_conteudo)

    send_mail(
        assunto,
        texto_conteudo,
        settings.EMAIL_HOST_USER,
        [user_email],
        html_message=html_conteudo
    )


# Finaliza o pedido com opção de pagamento em PIX ou Dinheiro
@login_required
def finalizar_pedido(request):
    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('lista_produtos')

    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo_entrega = request.POST.get('tipo_entrega')
        forma_pagamento = request.POST.get('forma_pagamento', 'pix')
        rua = request.POST.get('rua') or ''
        numero = request.POST.get('numero') or ''
        complemento = request.POST.get('complemento') or ''
        bairro = request.POST.get('bairro') or ''
        cpf = request.POST.get("cpf")

        total = Decimal('0.00')
        for produto_id, quantidade in carrinho.items():
            produto = Produto.objects.get(id=produto_id)
            subtotal = produto.preco * quantidade
            total += subtotal

        if tipo_entrega == 'delivery':
            total += Decimal('10.00')

        pedido = Pedido.objects.create(
            nome=nome,
            rua=rua,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            valor_total=total,
            tipo_entrega=tipo_entrega,
        )

        for produto_id, quantidade in carrinho.items():
            produto = Produto.objects.get(id=produto_id)
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco=produto.preco
            )

        # 💵 Se o pagamento for em dinheiro, apenas salva o pedido e redireciona
        if forma_pagamento == 'dinheiro':
            pedido.pago = True
            pedido.save()

            enviar_email_confirmacao(pedido, request.user.email)

            request.session['carrinho'] = {}
            return redirect('pagamento_sucesso')

        # 💳 Se for PIX, continua com integração Asaas
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
            pix_copia_cola = pagamento.get("pixCopyPaste") or pagamento.get("invoiceUrl")
            payment_id = pagamento.get("id")

            if settings.DEBUG and payment_id:
                #threading.Thread(target=simular_pagamento_automaticamente, args=(payment_id, pedido.id)).start()
                confirm_url = f"https://sandbox.asaas.com/api/v3/payments/{payment_id}/confirmPayment"
                confirm_resp = requests.post(confirm_url, headers=headers)
                print("Confirmação do pagamento:", confirm_resp.status_code, confirm_resp.text)
                #input()

                requests.post(confirm_url, headers=headers)
                threading.Thread(target=simular_pagamento_automaticamente, args=(payment_id, pedido.id)).start()



            pedido.asaas_id = payment_id
            pedido.save()

            enviar_email_confirmacao(pedido, request.user.email)

            qr_image = qrcode.make(pix_copia_cola)
            buffer = BytesIO()
            qr_image.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        except ValueError:
            messages.error(request, "Erro inesperado ao processar o pagamento.")
            return redirect("ver_carrinho")

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


# Simula o pagamento automático após 5 segundos ...:
def simular_pagamento_automaticamente(payment_id, pedido_id):
    time.sleep(5)
    url = f"https://sandbox.asaas.com/api/v3/payments/{payment_id}/receiveInCash"
    headers = {
        "Content-Type": "application/json",
        "access_token": "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmE4MDdhNWJiLWM1ZTktNGFhZi04MzlkLTE1NDYwZjY5YjgwZjo6JGFhY2hfYTA2MjM5NmItNzUwMi00MTU0LWIyODQtZjE5YTI4NmZlMDRm"}

    dados_pagamento = {
        "paymentDate": str(date.today()),
        "value": 10.00  # ou total real
    }

    response = requests.post(url, headers=headers, json=dados_pagamento)
    print("Simulação automática:", response.status_code, response.text)


    # Atualiza o pedido localmente ...:
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.pago = True
        pedido.save()
        print("Pagamento atualizado no banco local.")
    except Pedido.DoesNotExist:
        print("Pedido não encontrado para marcar como pago.")


# Verifica o status do pagamento do pedido ...:
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
    if request.method == 'POST':
        payload = json.loads(request.body)
        event = payload.get('event')
        payment_id = payload.get('payment', {}).get('id')
        status = payload.get('payment', {}).get('status')

        print(f"Evento: {event}")
        print(f"Pagamento ID: {payment_id}")
        print(f"Status: {status}")

        if status in ['RECEIVED', 'RECEIVED_IN_CASH']:
            try:
                pedido = Pedido.objects.get(asaas_id=payment_id)
                pedido.pago = True
                pedido.save()
                print("Pedido atualizado como pago.")
            except Pedido.DoesNotExist:
                print("Pedido não encontrado.")
        return HttpResponse(status=200)
    return HttpResponse(status=405)



def pagamento_sucesso(request):
    return render(request, 'cafeteria/pagamento_sucesso.html')





@login_required
def perfil_usuario(request):
    try:
        perfil = request.user.perfil
    except ObjectDoesNotExist:
        messages.warning(request, "Complete seu perfil antes de continuar.")
        return redirect('registro')  # Ou crie uma página apropriada para criação do perfil

    if request.method == 'POST':
        perfil.nome = request.POST.get('nome')
        perfil.cpf = request.POST.get('cpf')
        perfil.celular = request.POST.get('celular')

        data_str = request.POST.get('data_nascimento')
        try:
            perfil.data_nascimento = datetime.strptime(data_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Data de nascimento inválida.")
            return redirect('perfil_usuario')

        perfil.save()

        request.user.email = request.POST.get('email')
        request.user.save()

        messages.success(request, "Perfil atualizado com sucesso!")

    return render(request, 'cafeteria/perfil.html', {'perfil': perfil})





























