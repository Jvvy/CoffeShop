from django.shortcuts import render
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Produto

# View Home
def home(request):
    return render(request, 'cafeteria/home.html')

# Criação da View Produto ...:
def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'cafeteria/lista.html', {'produtos': produtos})


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


# Faz o login OBRIGATÓRIO ...:
@login_required
def lista_produtos(request):
    # só acessa se estiver logado
    produtos = Produto.objects.all()
    return render(request, 'cafeteria/lista.html', {'produtos': produtos})



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
