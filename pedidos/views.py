from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from .models import Pedido, DetallesPedido, BackOrder, Almacen
from .serializers import PedidoSerializer, BackOrderSerializer
from .forms import PedidoForm, AlmacenForm

@login_required(login_url='admin:login')
@permission_required('pedidos.view_pedido', raise_exception=True)
def listar_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'pedidos_list.html', {'pedidos': pedidos})

@login_required(login_url='admin:login')
@permission_required('pedidos.add_pedido', raise_exception=True)
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_pedidos')
    else:
        form = PedidoForm()
    return render(request, 'pedidos_form.html', {'form': form})

@login_required(login_url='admin:login')
@permission_required('pedidos.change_pedido', raise_exception=True)
def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        print("Form errors:", form.errors)
        if form.is_valid():
            print("POST data:", request.POST)
            form.save()
            
            # Si el estado cambió a entregado, inicializar pendiente = cantidad
            if pedido.estado == 'entregado':
                detalles = pedido.detalles.all()
                for detalle in detalles:
                    if detalle.pendiente == 0:
                        detalle.pendiente = detalle.cantidad
                        detalle.save()
            
            # Procesa los valores de Recibido, Pendiente, Folio
            detalles = pedido.detalles.all()
            for detalle in detalles:
                recibido_key = f'recibido_{detalle.id}'
                pendiente_key = f'pendiente_{detalle.id}'
                folio_key = f'folio_{detalle.id}'
                
                if recibido_key in request.POST:
                    detalle.recibido = request.POST.get(recibido_key, 0)
                if pendiente_key in request.POST:
                    detalle.pendiente = request.POST.get(pendiente_key, 0)
                if folio_key in request.POST:
                    detalle.folio_factura = request.POST.get(folio_key, '')
                
                detalle.save()
            
            # Crear o actualizar BackOrder automáticamente
            detalles = pedido.detalles.all()
            for detalle in detalles:
                if detalle.pendiente > 0:
                    backorder, created = BackOrder.objects.get_or_create(
                        pedido=pedido,
                        producto=detalle.producto,
                        almacen=detalle.almacen,
                        defaults={
                            'orden_compra': pedido.orden_compra,
                            'cantidad': detalle.cantidad,
                            'entregado': detalle.recibido,
                            'resuelto': False
                        }
                    )
                    if not created:
                        backorder.entregado = detalle.recibido
                        backorder.cantidad = detalle.cantidad
                        backorder.save()
                else:
                    BackOrder.objects.filter(
                        pedido=pedido,
                        producto=detalle.producto,
                        almacen=detalle.almacen
                    ).delete()
            
            return redirect('listar_pedidos')
    else:
        form = PedidoForm(instance=pedido)
    
    detalles = pedido.detalles.all()
    return render(request, 'pedidos_form.html', {
        'form': form, 
        'pedido': pedido,
        'detalles': detalles
    })
"""
@login_required(login_url='admin:login')
@permission_required('pedidos.change_pedido', raise_exception=True)
def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        print("Form errors:", form.errors)  # <-- Agrega ESTO
        if form.is_valid():
            print("POST data:", request.POST)  # <-- Agrega esta línea
            form.save()

            # Si el estado cambió a entregado, inicializar pendiente = cantidad
    if pedido.estado == 'entregado':
        detalles = pedido.detalles.all()
        for detalle in detalles:
            if detalle.pendiente == 0:  # Solo si es 0
                detalle.pendiente = detalle.cantidad  # Lo pone igual a cantidad
                detalle.save()
            
            # Procesa los valores de Recibido, Pendiente, Folio
            detalles = pedido.detalles.all()
            for detalle in detalles:
                # Busca si vienen valores en el POST
                recibido_key = f'recibido_{detalle.id}'
                pendiente_key = f'pendiente_{detalle.id}'
                folio_key = f'folio_{detalle.id}'
                
                if recibido_key in request.POST:
                    detalle.recibido = request.POST.get(recibido_key, 0)
                if pendiente_key in request.POST:
                    detalle.pendiente = request.POST.get(pendiente_key, 0)
                if folio_key in request.POST:
                    detalle.folio_factura = request.POST.get(folio_key, '')
                
                detalle.save()
            
            return redirect('listar_pedidos')
    else:
        form = PedidoForm(instance=pedido)
    
    detalles = pedido.detalles.all()
    return render(request, 'pedidos_form.html', {
        'form': form, 
        'pedido': pedido,
        'detalles': detalles
    })
"""
@login_required(login_url='admin:login')
@permission_required('pedidos.delete_pedido', raise_exception=True)
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.delete()
    return redirect('listar_pedidos')

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class BackOrderViewSet(viewsets.ModelViewSet):
    queryset = BackOrder.objects.all()
    serializer_class = BackOrderSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

@login_required(login_url='admin:login')
@permission_required('pedidos.view_almacen', raise_exception=True)
def listar_almacenes(request):
    almacenes = Almacen.objects.all()
    return render(request, 'almacenes_list.html', {'almacenes': almacenes})

@login_required(login_url='admin:login')
@permission_required('pedidos.add_almacen', raise_exception=True)
def crear_almacen(request):
    if request.method == 'POST':
        form = AlmacenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_almacenes')
    else:
        form = AlmacenForm()
    return render(request, 'almacenes_form.html', {'form': form, 'titulo': 'Crear Almacén'})

@login_required(login_url='admin:login')
@permission_required('pedidos.change_almacen', raise_exception=True)
def editar_almacen(request, almacen_id):
    almacen = get_object_or_404(Almacen, id=almacen_id)
    if request.method == 'POST':
        form = AlmacenForm(request.POST, instance=almacen)
        if form.is_valid():
            form.save()
            return redirect('listar_almacenes')
    else:
        form = AlmacenForm(instance=almacen)
    return render(request, 'almacenes_form.html', {'form': form, 'titulo': 'Editar Almacén'})

@login_required(login_url='admin:login')
@permission_required('pedidos.delete_almacen', raise_exception=True)
def eliminar_almacen(request, almacen_id):
    almacen = get_object_or_404(Almacen, id=almacen_id)
    almacen.delete()
    return redirect('listar_almacenes')