from django.shortcuts import render
from .models import Produto
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


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
