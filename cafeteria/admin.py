from django.contrib import admin
from .models import Produto,Pedido, ItemPedido


# Admin Registrado ...:
admin.site.register(Produto)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'data')
    inlines = [ItemPedidoInline]

admin.site.register(Pedido, PedidoAdmin)
