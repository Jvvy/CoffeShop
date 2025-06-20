import os
from pathlib import Path


# Base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent


# Segurança
SECRET_KEY = 'sua-secret-key-aqui'
DEBUG = True


# Aplicações instaladas ...:
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cafeteria',  # App Adicionado ...:
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meu_site.urls'


# Configuração dos templates ...:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cafeteria.context_processors.total_itens_carrinho',
            ],
        },
    },
]

# Configuração do WSGI (Web Server Gateway Interface) ...:
WSGI_APPLICATION = 'meu_site.wsgi.application'


# Banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validações de senha (Gambi na Mão para mudar a mensagem) ...:
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'cafeteria.validators.ValidadorMinimoPersonalizado',
        'OPTIONS': {
            'min_length': 8
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configurações de autenticação ...:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jv.cl2017@gmail.com' # Mudar aqui colcoar com hash
EMAIL_HOST_PASSWORD = 'pcwr ezca phsc gggo' # Mudar aqui colcoar com hash


# Idioma e horário ...:
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configurações de arquivos estáticos (CSS, JS, imagens fixas) ...:
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


#  Configurações de arquivos enviados pelos usuários (imagens, uploads) ...:
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Padrão para chaves primárias ...:
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Redirecionamento correto de login ...:
LOGIN_URL = '/login/'


# Rota de Logout ...:
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'


# Configurações de segurança ...:
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'e82c-177-137-5-94.ngrok-free.app'
    
]