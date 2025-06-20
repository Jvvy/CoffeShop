from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.templatetags.static import static
from .models import Produto, Pedido, ItemPedido, Perfil

# 🎨 Personalização do cabeçalho e título do site admin
admin.site.site_header = "Painel Administrador The Best Coffee"
admin.site.site_title = "The Best Coffee Admin"
admin.site.index_title = "Bem-vindo ao Painel de Administração"


# Injecta CSS customizado no admin
def custom_admin_css():
    return format_html('<link rel="stylesheet" type="text/css" href="{}">', static('admin/css/custom_admin.css'))


# Admin Produto
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'preco')
    search_fields = ('nome',)


# Inline dos itens do pedido ...:
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0

# Admin Pedido ...:
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'tipo_entrega', 'rua', 'numero', 'bairro', 'pago', 'criado_em')
    list_filter = ('pago', 'bairro', 'tipo_entrega', 'criado_em')
    search_fields = ('nome', 'bairro', 'rua')
    inlines = [ItemPedidoInline]
    readonly_fields = ('criado_em',)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

# Inline do Perfil (para aparecer dentro do admin do User) ...:
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'

# Admin User customizado para exibir dados do perfil ...:
class UserAdminCustom(UserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'mostrar_nome_completo', 'is_staff', 'cpf', 'celular')
    list_select_related = ('perfil',)
    search_fields = ('username', 'email', 'perfil__nome', 'perfil__cpf')

    def mostrar_nome_completo(self, obj):
        try:
            return obj.perfil.nome
        except Perfil.DoesNotExist:
            return "-"
    mostrar_nome_completo.short_description = 'Nome Completo'

    def cpf(self, obj):
        try:
            return obj.perfil.cpf
        except Perfil.DoesNotExist:
            return "-"
    
    def celular(self, obj):
        try:
            return obj.perfil.celular
        except Perfil.DoesNotExist:
            return "-"

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

# Re-registrar User com o admin customizado ...:
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
