from django.contrib import admin
from .models import Pedido, DetallesPedido, BackOrder, Almacen, BackOrderInterno
from django import forms
from django.contrib import messages
from .historial import registrar, registrar_exportacion
from productos.models import Producto

import datetime
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
import unicodedata
from django.urls import path
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.admin.models import ADDITION
from proveedores.models import Proveedor


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

class ExcelImportForm(forms.Form):
    archivo = forms.FileField(label='Archivo de Excel (.xlsx)')


def _normalizar(texto):
    """Quita acentos y mayúsculas para comparar encabezados."""
    t = unicodedata.normalize('NFKD', str(texto or '')).encode('ascii', 'ignore').decode()
    return t.strip().lower()



@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'proveedor', 'estado', 'fecha_pedido')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('numero_pedido', 'proveedor__nombre')
    inlines = [DetallesPedidoInline]
    actions = [exportar_pedidos]
    change_list_template = 'admin/pedidos_change_list.html'
    
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

    def get_urls(self):
        urls = super().get_urls()
        propias = [
            path('importar-excel/', self.admin_site.admin_view(self.importar_excel),
                 name='pedido_importar_excel'),
        ]
        return propias + urls

    def importar_excel(self, request):
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    pedido, resueltos = self._crear_pedido_desde_excel(request, request.FILES['archivo'])
                except ValueError as e:
                    messages.error(request, f'❌ No se importó nada. {e}')
                    return redirect('.')
                messages.success(request,
                    f'✅ Pedido {pedido.numero_pedido} creado en Pendiente con '
                    f'{pedido.detalles.count()} producto(s). '
                    f'{resueltos} Back Order(s) Interno(s) marcados como resueltos.')
                return redirect(f'../{pedido.pk}/change/')
        else:
            form = ExcelImportForm()
        context = {
            **self.admin_site.each_context(request),
            'form': form,
            'title': 'Importar pedido desde Excel',
            'opts': self.model._meta,
        }
        return render(request, 'admin/pedidos_import_excel.html', context)

    def _crear_pedido_desde_excel(self, request, archivo):
        if not archivo.name.lower().endswith('.xlsx'):
            raise ValueError('El archivo debe ser de Excel (.xlsx).')
        try:
            hoja = load_workbook(archivo, data_only=True).active
        except Exception:
            raise ValueError('No se pudo leer el archivo de Excel.')

        filas = list(hoja.iter_rows(values_only=True))
        if not filas:
            raise ValueError('El archivo está vacío.')

        # Ubicar las columnas por su nombre
        encabezados = [_normalizar(c) for c in filas[0]]
        requeridas = {'proveedor': 'Proveedor', 'pedido origen': 'Pedido origen',
                      'producto': 'Producto', 'almacen': 'Almacén', 'cantidad': 'Cantidad'}
        faltan = [nombre for clave, nombre in requeridas.items() if clave not in encabezados]
        if faltan:
            raise ValueError('Faltan columnas: ' + ', '.join(faltan))
        col = {clave: encabezados.index(clave) for clave in requeridas}

        def valor(fila, clave):
            i = col[clave]
            v = fila[i] if i < len(fila) else None
            return '' if v is None else str(v).strip()

        datos = []
        for num, fila in enumerate(filas[1:], start=2):
            if not fila or all(v in (None, '') for v in fila):
                continue  # fila vacía
            datos.append((num, valor(fila, 'proveedor'), valor(fila, 'pedido origen'),
                          valor(fila, 'producto'), valor(fila, 'almacen'), valor(fila, 'cantidad')))
        if not datos:
            raise ValueError('El archivo no tiene productos.')

        # Un solo proveedor y un solo número de pedido
        provs = {d[1].upper() for d in datos}
        if len(provs) != 1:
            raise ValueError('El archivo trae más de un proveedor: ' + ', '.join(sorted(provs)))
        numeros = {d[2].upper() for d in datos}
        if len(numeros) != 1:
            raise ValueError('"Pedido origen" debe tener el mismo número en todas las filas.')
        numero = numeros.pop()
        if len(numero) < 5:
            raise ValueError('El número de pedido debe tener al menos 5 caracteres.')

        proveedor = Proveedor.objects.filter(nombre__iexact=datos[0][1]).first()
        if not proveedor:
            raise ValueError(f'No existe el proveedor "{datos[0][1]}".')
        if Pedido.objects.filter(numero_pedido__iexact=numero).exists():
            raise ValueError(f'Ya existe un pedido con el número "{numero}".')

        # Revisar productos, almacenes y cantidades
        errores, renglones = [], {}
        for num, _, _, prod, alm, cant in datos:
            problemas = []
            producto = Producto.objects.filter(nombre__iexact=prod).first()
            almacen = Almacen.objects.filter(nombre__iexact=alm).first() if alm else None
            if not producto:
                problemas.append(f'fila {num}: el producto "{prod}" no existe')
            if alm and not almacen:
                problemas.append(f'fila {num}: el almacén "{alm}" no existe')
            try:
                cantidad = int(float(cant))
            except ValueError:
                cantidad = 0
            if cantidad <= 0:
                problemas.append(f'fila {num}: la cantidad "{cant}" no es válida')
            if problemas:
                errores += problemas
                continue
            clave = (producto.pk, almacen.pk if almacen else None)
            if clave in renglones:
                renglones[clave][2] += cantidad   # repetido: se suma
            else:
                renglones[clave] = [producto, almacen, cantidad]
        if errores:
            raise ValueError('Errores: ' + ' | '.join(errores[:15]) + (' ...' if len(errores) > 15 else ''))

        # Crear todo (o nada)
        with transaction.atomic():
            pedido = Pedido.objects.create(numero_pedido=numero, proveedor=proveedor,
                                           estado='pendiente')
            resueltos = 0
            for producto, almacen, cantidad in renglones.values():
                DetallesPedido.objects.create(pedido=pedido, producto=producto,
                                              almacen=almacen, cantidad=cantidad)
                resueltos += BackOrderInterno.objects.filter(
                    resuelto=False, proveedor=proveedor, producto=producto, almacen=almacen,
                ).update(resuelto=True)
            registrar(request, pedido,
                      f'Creó el pedido desde Excel con {len(renglones)} producto(s); '
                      f'resolvió {resueltos} Back Order(s) Interno(s)', ADDITION)
        return pedido, resueltos






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
