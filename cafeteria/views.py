from django.shortcuts import render
from .models import Produto



# Criação da View Produto ...:
def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'cafeteria/lista.html', {'produtos': produtos})