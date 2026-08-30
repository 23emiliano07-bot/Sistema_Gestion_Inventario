from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets

from .models import Pedido, BackOrder
from .serializers import PedidoSerializer, BackOrderSerializer
from .forms import PedidoForm

def listar_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'pedidos_list.html', {'pedidos': pedidos})

def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_pedidos')
    else:
        form = PedidoForm()
    return render(request, 'pedidos_form.html', {'form': form})

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

def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.delete()
    return redirect('listar_pedidos')

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class BackOrderViewSet(viewsets.ModelViewSet):
    queryset = BackOrder.objects.all()
    serializer_class = BackOrderSerializer