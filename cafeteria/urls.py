from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registrar_usuario,lista_produtos,home

urlpatterns = [
    path('', home, name='home'),
    path('cardapio/', lista_produtos, name='lista_produtos'), 
    path('login/', auth_views.LoginView.as_view(template_name='cafeteria/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', registrar_usuario, name='registro'),
]
