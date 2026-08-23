from django.contrib import admin
from .models import Pedido, BackOrder

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'proveedor', 'producto', 'cantidad', 'estado', 'fecha_pedido')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('numero_pedido', 'proveedor__nombre')

@admin.register(BackOrder)
class BackOrderAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'cantidad_pendiente', 'resuelto', 'fecha_creacion')
    list_filter = ('resuelto',)