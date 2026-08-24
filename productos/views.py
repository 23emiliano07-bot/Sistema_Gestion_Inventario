from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Producto
# TODO: Resolver import circular - from .dao.producto_dao import ProductoDAO
from .serializers import ProductoSerializer
from .forms import ProductoForm

# VISTAS WEB
def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos_list.html', {'productos': productos})

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos_form.html', {'form': form})

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos_form.html', {'form': form, 'producto': producto})

def desactivar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.disponible = False
    producto.save()
    return redirect('listar_productos')

# API REST
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer