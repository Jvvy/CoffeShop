from django.contrib import admin
from .models import Produto, Pedido, ItemPedido

# Admin Produto
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'preco')
    search_fields = ('nome',)

# Inline dos itens do pedido
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0

# Admin Pedido
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'rua', 'numero', 'bairro', 'pago', 'criado_em')
    list_filter = ('pago', 'bairro', 'criado_em')
    search_fields = ('nome', 'bairro', 'rua')
    inlines = [ItemPedidoInline]
    readonly_fields = ('criado_em',)
