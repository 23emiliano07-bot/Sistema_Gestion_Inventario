from django.contrib import admin
from .models import Pedido, DetallesPedido, BackOrder, Almacen

class DetallesPedidoInline(admin.TabularInline):
    model = DetallesPedido
    extra = 1
    fields = ('producto', 'almacen', 'cantidad', 'precio_unitario', 'recibido', 'pendiente', 'folio_factura')
    readonly_fields = ('precio_unitario',)
    
    def get_readonly_fields(self, request, obj=None):
        readonly = ['precio_unitario']
        if obj and obj.estado != 'entregado':
            readonly.extend(['recibido', 'pendiente', 'folio_factura'])
        return readonly

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'fecha_creacion')
    search_fields = ('nombre',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'proveedor', 'estado', 'fecha_pedido')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('numero_pedido', 'proveedor__nombre')
    inlines = [DetallesPedidoInline]
    
    def get_readonly_fields(self, request, obj=None):
        readonly = []
        if obj:
            if obj.estado == 'pendiente':
                readonly = ['orden_compra', 'orden_venta', 'responsable', 'numero_pedido', 'proveedor']
            elif obj.estado == 'confirmado':
                readonly = ['responsable', 'numero_pedido', 'proveedor']
            elif obj.estado == 'solicitado':
                readonly = ['numero_pedido', 'proveedor', 'orden_compra', 'orden_venta']
            elif obj.estado == 'entregado':
                readonly = ['numero_pedido', 'proveedor', 'orden_compra', 'orden_venta', 'responsable', 'estado']
        return readonly

@admin.register(DetallesPedido)
class DetallesPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'almacen', 'cantidad', 'recibido', 'pendiente')
    list_filter = ('pedido__fecha_pedido',)
    search_fields = ('pedido__numero_pedido', 'producto__nombre')

from django.contrib import admin
from .models import BackOrder

@admin.register(BackOrder)
class BackOrderAdmin(admin.ModelAdmin):
    list_display = ('get_proveedor', 'orden_compra', 'producto', 'almacen', 'cantidad', 'entregado', 'resuelto', 'fecha_creacion')
    list_filter = ('resuelto', 'fecha_creacion', 'pedido__proveedor__nombre')
    search_fields = ('pedido__numero_pedido', 'producto__nombre', 'pedido__proveedor__nombre')
    readonly_fields = ('get_proveedor', 'orden_compra', 'producto', 'almacen', 'cantidad')
    
    def get_proveedor(self, obj):
        return obj.pedido.proveedor
    get_proveedor.short_description = 'Proveedor'
