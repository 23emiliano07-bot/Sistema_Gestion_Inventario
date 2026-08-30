from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from .models import Pedido, BackOrder
from .serializers import PedidoSerializer, BackOrderSerializer
from .forms import PedidoForm

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
        if form.is_valid():
            form.save()
            return redirect('listar_pedidos')
    else:
        form = PedidoForm(instance=pedido)
    
    detalles = pedido.detalles.all()
    return render(request, 'pedidos_form.html', {
        'form': form, 
        'pedido': pedido,
        'detalles': detalles
    })

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