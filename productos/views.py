from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from .models import Producto
# TODO: Resolver import circular - from .dao.producto_dao import ProductoDAO
from .serializers import ProductoSerializer
from .forms import ProductoForm

# VISTAS WEB
@login_required(login_url='admin:login')
@permission_required('productos.view_producto', raise_exception=True)
def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos_list.html', {'productos': productos})

@login_required(login_url='admin:login')
@permission_required('productos.add_producto', raise_exception=True)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)  # ← Agregado request.FILES para imagen
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos_form.html', {'form': form})

@login_required(login_url='admin:login')
@permission_required('productos.change_producto', raise_exception=True)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)  # ← Agregado request.FILES
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos_form.html', {'form': form, 'producto': producto})

@login_required(login_url='admin:login')
@permission_required('productos.change_producto', raise_exception=True)
def desactivar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.disponible = False
    producto.save()
    return redirect('listar_productos')

# API REST
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]