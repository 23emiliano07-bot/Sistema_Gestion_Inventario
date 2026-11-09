from django.contrib import admin
from .models import Pedido, DetallesPedido, BackOrder, Almacen, BackOrderInterno
from django import forms
from django.contrib import messages
from .historial import registrar, registrar_exportacion
from productos.models import Producto

import datetime
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def _fecha(f):
    """Excel no acepta fechas con zona horaria: la pasamos a hora de México."""
    if isinstance(f, datetime.datetime) and timezone.is_aware(f):
        return timezone.localtime(f).replace(tzinfo=None)
    return f or ''


def generar_excel(nombre, encabezados, filas):
    wb = Workbook()
    ws = wb.active
    ws.title = nombre[:31]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True, color='FFFFFF')
        celda.fill = PatternFill('solid', fgColor='1F3A5F')
    for fila in filas:
        ws.append(fila)
    for row in ws.iter_rows(min_row=2):
        for celda in row:
            if isinstance(celda.value, datetime.datetime):
                celda.number_format = 'DD/MM/YYYY HH:MM'
    for col in ws.columns:
        ancho = max(len(str(c.value or '')) for c in col)
        ws.column_dimensions[col[0].column_letter].width = min(ancho + 2, 60)
    ws.freeze_panes = 'A2'

    hoy = timezone.localtime().strftime('%Y-%m-%d')
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="{nombre}_{hoy}.xlsx"'
    wb.save(resp)
    return resp


@admin.action(description='📥 Exportar a Excel')
def exportar_pedidos(modeladmin, request, queryset):
    encabezados = ['Pedido', 'Proveedor', 'Estado', 'Fecha', 'Orden compra', 'Orden venta',
                   'Responsable', 'Recibió', 'Producto', 'Descripción', 'Almacén', 'Cantidad',
                   'Recibido', 'Pendiente', 'Folio factura']
    filas = []
    pedidos = queryset.select_related('proveedor', 'responsable', 'responsable_recibio').prefetch_related(
        'detalles__producto', 'detalles__almacen')
    for p in pedidos:
        base = [p.numero_pedido, p.proveedor.nombre, p.get_estado_display(),
                _fecha(p.fecha_pedido), p.orden_compra or '', p.orden_venta or '',
                str(p.responsable or ''), str(p.responsable_recibio or '')]
        detalles = list(p.detalles.all())
        if not detalles:
            filas.append(base + [''] * 7)
        for d in detalles:
            filas.append(base + [
                d.producto.nombre if d.producto else '',
                (d.producto.descripcion or '') if d.producto else '',
                str(d.almacen or ''), d.cantidad, d.recibido, d.pendiente,
                d.folio_factura or '',
            ])
    registrar_exportacion(request, queryset, 'Pedidos')
    return generar_excel('Pedidos', encabezados, filas)


@admin.action(description='📥 Exportar a Excel')
def exportar_backorders(modeladmin, request, queryset):
    encabezados = ['Proveedor', 'Pedido', 'Orden compra', 'Producto', 'Descripción',
                   'Almacén', 'Cantidad', 'Entregado', 'Faltante', 'Resuelto', 'Fecha']
    filas = []
    for b in queryset.select_related('pedido__proveedor', 'producto', 'almacen'):
        filas.append([
            b.pedido.proveedor.nombre, b.pedido.numero_pedido, b.orden_compra or '',
            b.producto.nombre if b.producto else '',
            (b.producto.descripcion or '') if b.producto else '',
            str(b.almacen or ''), b.cantidad, b.entregado, b.cantidad - b.entregado,
            'Sí' if b.resuelto else 'No', _fecha(b.fecha_creacion),
        ])
    registrar_exportacion(request, queryset, 'Back Orders')
    return generar_excel('BackOrders', encabezados, filas)
    

class DetallesPedidoInlineForm(forms.ModelForm):
    # Casilla solo del formulario (no se guarda en la base de datos)
    pendiente_orden = forms.BooleanField(required=False, label='Pendiente orden')

    class Meta:
        model = DetallesPedido
        fields = '__all__'


class DetallesPedidoInline(admin.TabularInline):
    model = DetallesPedido
    form = DetallesPedidoInlineForm
    extra = 1
    raw_id_fields = ('producto',)

    def get_fields(self, request, obj=None):
        campos = ['producto', 'almacen', 'cantidad']
        if obj and obj.estado == 'confirmado':
            campos.append('pendiente_orden')   # en lugar de Precio unitario
        return campos + ['recibido', 'pendiente', 'folio_factura']

    def get_readonly_fields(self, request, obj=None):
        readonly = []
        # En Solicitado, Entregado y Finalizado ya no se cambian los productos
        if obj and obj.estado in ('solicitado', 'entregado', 'finalizado'):
            readonly += ['producto', 'almacen', 'cantidad']
        # Recibido, Pendiente y Folio solo se editan en Entregado
        if obj and obj.estado != 'entregado':
            readonly += ['recibido', 'pendiente', 'folio_factura']
        return readonly

    def has_delete_permission(self, request, obj=None):
        # Solo se pueden quitar productos en estado Pendiente
        if obj is None or obj.estado == 'pendiente':
            return super().has_delete_permission(request, obj)
        return False

    def has_add_permission(self, request, obj=None):
        # Solo se pueden agregar productos en estado Pendiente
        if obj is None or obj.estado == 'pendiente':
            return super().has_add_permission(request, obj)
        return False
    
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
    actions = [exportar_pedidos]
    
    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ['responsable_recibio']
        if obj.estado == 'pendiente':
            return ['orden_compra', 'orden_venta', 'responsable', 'numero_pedido',
                    'proveedor', 'responsable_recibio']
        if obj.estado == 'confirmado':
            return ['responsable', 'numero_pedido', 'proveedor', 'orden_venta',
                    'responsable_recibio']
        if obj.estado == 'solicitado':
            return ['numero_pedido', 'proveedor', 'orden_compra', 'responsable_recibio']
        if obj.estado == 'entregado':
            return ['numero_pedido', 'proveedor', 'orden_compra', 'orden_venta',
                    'responsable', 'estado']
        if obj.estado == 'finalizado':
            return ['numero_pedido', 'proveedor', 'estado', 'notas', 'orden_compra',
                    'orden_venta', 'responsable', 'responsable_recibio']
        return []
    
    SIGUIENTE = {
        'pendiente': 'confirmado',
        'confirmado': 'solicitado',
        'solicitado': 'entregado',
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'estado' in form.base_fields:
            if obj is None:
                permitidos = ['pendiente']
            else:
                permitidos = [obj.estado]
                if obj.estado in self.SIGUIENTE:
                    permitidos.append(self.SIGUIENTE[obj.estado])
            campo = form.base_fields['estado']
            campo.choices = [(k, v) for k, v in campo.choices if k in permitidos]
        return form

    def save_model(self, request, obj, form, change):
        anterior = Pedido.objects.get(pk=obj.pk).estado if change else None
        super().save_model(request, obj, form, change)
        if change and anterior != obj.estado:
            nombres = dict(Pedido._meta.get_field('estado').choices)
            registrar(request, obj, f'Estado: {nombres.get(anterior)} → {nombres.get(obj.estado)} (Admin)')
    
    def save_formset(self, request, form, formset, change):
        if formset.model is not DetallesPedido:
            return super().save_formset(request, form, formset, change)

        # Productos marcados como "Pendiente orden"
        mover = [
            f.instance for f in formset.forms
            if f.instance.pk
            and f.cleaned_data.get('pendiente_orden')
            and not f.cleaned_data.get('DELETE')
        ]
        super().save_formset(request, form, formset, change)

        pedido = form.instance
        for d in mover:
            BackOrderInterno.objects.create(
                pedido_origen=pedido,
                proveedor=pedido.proveedor,
                numero_pedido=pedido.numero_pedido,
                orden_compra=pedido.orden_compra,
                producto=d.producto,
                almacen=d.almacen,
                cantidad=d.cantidad,
                creado_por=request.user,
            )
            registrar(request, pedido, f'Movió a Back Order Interno: {d.producto.nombre} ({d.cantidad})')   # ← NUEVA
            d.delete()

        if mover:
            messages.info(request, f'📦 {len(mover)} producto(s) movido(s) a Back Order Interno.')

        # Si todo está recibido (pendiente 0), pasa a Finalizado
        if pedido.revisar_finalizado():
            registrar(request, pedido, 'Estado: Entregado → Finalizado (automático)')
            messages.success(request, '✅ El pedido pasó a Finalizado: todo fue recibido.')

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
    actions = [exportar_backorders]
    
    def get_proveedor(self, obj):
        return obj.pedido.proveedor
    get_proveedor.short_description = 'Proveedor'

@admin.action(description='📥 Exportar a Excel')
def exportar_backorders_internos(modeladmin, request, queryset):
    encabezados = ['Proveedor', 'Pedido origen', 'Orden compra', 'Producto', 'Descripción',
                   'Almacén', 'Cantidad', 'Recibido', 'Pendiente', 'Folio factura',
                   'Resuelto', 'Creado por', 'Fecha']
    filas = []
    for b in queryset.select_related('proveedor', 'producto', 'almacen', 'creado_por'):
        filas.append([
            b.proveedor.nombre if b.proveedor else '', b.numero_pedido,
            b.orden_compra or '', b.producto.nombre, b.producto.descripcion or '',
            str(b.almacen or ''), b.cantidad, b.recibido, b.pendiente,
            b.folio_factura or '', 'Sí' if b.resuelto else 'No',
            str(b.creado_por or ''), _fecha(b.fecha_creacion),
        ])
    registrar_exportacion(request, queryset, 'Back Orders Internos')
    return generar_excel('BackOrdersInternos', encabezados, filas)


@admin.action(description='↩️ Regresar al pedido')
def regresar_al_pedido(modeladmin, request, queryset):
    regresados, omitidos = 0, []
    for b in queryset.select_related('pedido_origen', 'producto'):
        p = b.pedido_origen
        # Solo si el pedido sigue en Confirmado y el BOI no está resuelto
        if not p or p.estado != 'confirmado' or b.resuelto:
            omitidos.append(f'{b.producto.nombre} ({b.numero_pedido})')
            continue
        detalle, creado = DetallesPedido.objects.get_or_create(
            pedido=p, producto=b.producto, almacen=b.almacen,
            defaults={'cantidad': b.cantidad},
        )
        if not creado:   # si ya estaba en el pedido, se suma la cantidad
            detalle.cantidad += b.cantidad
            detalle.save()
        registrar(request, p, f'Regresó del Back Order Interno: {b.producto.nombre} ({b.cantidad})')    
        b.delete()
        regresados += 1

    if regresados:
        messages.success(request, f'↩️ {regresados} producto(s) regresado(s) a su pedido.')
    if omitidos:
        messages.warning(request, '⚠️ No se regresaron (el pedido ya no está en Confirmado '
                                  'o el back order está resuelto): ' + ', '.join(omitidos))


@admin.register(BackOrderInterno)
class BackOrderInternoAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'numero_pedido', 'orden_compra', 'producto', 'almacen',
                    'cantidad', 'recibido', 'pendiente', 'folio_factura', 'resuelto',
                    'fecha_creacion')
    list_filter = ('resuelto', 'proveedor', 'almacen', 'fecha_creacion')
    search_fields = ('producto__nombre', 'numero_pedido', 'orden_compra', 'proveedor__nombre')
    fields = ('pedido_origen', 'proveedor', 'numero_pedido', 'orden_compra', 'producto',
              'almacen', 'cantidad', 'recibido', 'pendiente', 'folio_factura', 'resuelto',
              'creado_por', 'fecha_creacion', 'fecha_actualizacion')
    readonly_fields = ('pedido_origen', 'proveedor', 'numero_pedido', 'orden_compra',
                       'producto', 'almacen', 'cantidad', 'pendiente', 'creado_por',
                       'fecha_creacion', 'fecha_actualizacion')
    actions = [exportar_backorders_internos, regresar_al_pedido]

    def has_add_permission(self, request):
        # Solo se crean desde un pedido (casilla "Pendiente orden")
        return False

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION


@admin.register(LogEntry)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'accion', 'content_type', 'object_repr', 'detalle')
    list_filter = ('user', 'action_flag', 'content_type', 'action_time')
    search_fields = ('object_repr', 'change_message', 'user__username')
    date_hierarchy = 'action_time'
    list_per_page = 50

    def accion(self, obj):
        if (obj.change_message or '').startswith('📥'):
            return '📥 Exportó'
        return {ADDITION: '➕ Agregó', CHANGE: '✏️ Modificó',
                DELETION: '🗑️ Eliminó'}.get(obj.action_flag, '')
    accion.short_description = 'Acción'

    def detalle(self, obj):
        return obj.get_change_message()
    detalle.short_description = 'Detalle'

    # Solo lectura: nadie puede crear, editar ni borrar el historial
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
