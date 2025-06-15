from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registrar_usuario,lista_produtos,home
from . import views
from cafeteria.views import asaas_webhook
from cafeteria.forms import LoginEmailOuUsuarioForm


urlpatterns = [

    # URL para a página inicial ...:
    path('', home, name='home'),

    
    # URL para a página de produtos ...:
    path('cardapio/', lista_produtos, name='lista_produtos'), 
   
   
    # URL para Login e Logout ...:
    path('login/', auth_views.LoginView.as_view(template_name='cafeteria/login.html',authentication_form=LoginEmailOuUsuarioForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


    # URL para Registro de Usuário ...:
    path('registro/', registrar_usuario, name='registro'),


    # Itens Carrinho
    path('adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('alterar-quantidade/<int:produto_id>/', views.alterar_quantidade, name='alterar_quantidade'),


    # URL para atualizar a quantidade de produtos no carrinho ...:
    path('quantidade-carrinho/', views.quantidade_carrinho, name='quantidade_carrinho'),


    # URL para finalizar o pedido ...:
    path('finalizar/', views.finalizar_pedido, name='finalizar_pedido'),


    # URL para redefinir a senha ...:
    path('resetar-senha/', auth_views.PasswordResetView.as_view(template_name='cafeteria/reset_senha.html'), name='password_reset'),
    path('resetar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='cafeteria/reset_enviado.html'), name='password_reset_done'),
    path('resetar-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='cafeteria/reset_confirmar.html'), name='password_reset_confirm'),
    path('resetar-senha/feito/', auth_views.PasswordResetCompleteView.as_view(template_name='cafeteria/reset_completo.html'), name='password_reset_complete'),
    

    # URL para o webhook do Asaas ...:
    path('webhook/asaas/', views.asaas_webhook, name='asaas_webhook'),


    # URL para verificar o status do pagamento ...:
    path('verificar-status/<int:pedido_id>/', views.verificar_status_pagamento, name='verificar_status_pagamento'),
    path('pagamento-sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),


    # URL para o perfil do usuário ...:
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),

]
