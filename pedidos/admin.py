from django.contrib import admin
from .models import Pedido, DetallesPedido, BackOrder

class DetallesPedidoInline(admin.TabularInline):
    model = DetallesPedido
    extra = 1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'proveedor', 'estado', 'fecha_pedido', 'total_pedido')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('numero_pedido', 'proveedor__nombre')
    inlines = [DetallesPedidoInline]
    
    def total_pedido(self, obj):
        return f"${obj.total}"
    total_pedido.short_description = "Total"

@admin.register(DetallesPedido)
class DetallesPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('pedido__fecha_pedido',)
    search_fields = ('pedido__numero_pedido', 'producto__nombre')

@admin.register(BackOrder)
class BackOrderAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'cantidad_pendiente', 'resuelto', 'fecha_creacion')
    list_filter = ('resuelto',)