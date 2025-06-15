from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

# Formulário de autenticação personalizado para aceitar email ou nome de usuário ...:
class LoginEmailOuUsuarioForm(AuthenticationForm):
    username = forms.CharField(label="Usuário ou Email")

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(email=username)
                username = user.username
            except User.DoesNotExist:
                pass  # Tenta autenticar pelo username mesmo

            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Usuário ou senha inválidos."))

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


# RegistroForm para cadastro de usuários personalizado ...:
class RegistroForm(UserCreationForm):
    nome = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='Email')
    cpf = forms.CharField(label='CPF', max_length=14)
    data_nascimento = forms.DateField(label='Data de nascimento', widget=forms.DateInput(attrs={'type': 'date'}))
    celular = forms.CharField(label='Celular', max_length=15)

    class Meta:
        model = User
        fields = ['username', 'nome', 'email', 'cpf', 'data_nascimento', 'celular', 'password1', 'password2']


# Método de validação para o campo de email no RegistroForm ...:
def clean_email(self):
    email = self.cleaned_data.get('email')
    if not email:
        raise forms.ValidationError("Por favor, preencha o e-mail.")
    return email
