from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registrar_usuario,lista_produtos,home
from . import views

urlpatterns = [

    # URL para a página inicial ...:
    path('', home, name='home'),

    
    # URL para a página de produtos ...:
    path('cardapio/', lista_produtos, name='lista_produtos'), 
   
   
    # URL para Login e Logout ...:
    path('login/', auth_views.LoginView.as_view(template_name='cafeteria/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # URL para Registro de Usuário ...:
    path('registro/', registrar_usuario, name='registro'),

    # Itens Carrinho
    path('adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),

    # URL para atualizar a quantidade de produtos no carrinho ...:
    path('quantidade-carrinho/', views.quantidade_carrinho, name='quantidade_carrinho'),

    # URL para finalizar o pedido ...:
    path('finalizar/', views.finalizar_pedido, name='finalizar_pedido'),

    # URL para redefinir a senha ...:
    path('resetar-senha/', auth_views.PasswordResetView.as_view(template_name='cafeteria/reset_senha.html'), name='password_reset'),
    path('resetar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='cafeteria/reset_enviado.html'), name='password_reset_done'),
    path('resetar-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='cafeteria/reset_confirmar.html'), name='password_reset_confirm'),
    path('resetar-senha/feito/', auth_views.PasswordResetCompleteView.as_view(template_name='cafeteria/reset_completo.html'), name='password_reset_complete'),


]
