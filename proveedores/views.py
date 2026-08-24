from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Proveedor
# TODO: Resolver import circular - from .dao.proveedor_dao import ProveedorDAO
from .serializers import ProveedorSerializer
from .forms import ProveedorForm

# ============================================
# 1. VISTAS WEB (HTML)
# ============================================

def listar_proveedores(request):
    """Lista todos los proveedores activos"""
    proveedores = Proveedor.objects.filter(activo=True)
    return render(request, 'proveedores_list.html', {'proveedores': proveedores})

def crear_proveedor(request):
    """Crear un nuevo proveedor"""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'proveedores_form.html', {'form': form})

def editar_proveedor(request, proveedor_id):
    """Editar un proveedor existente"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('listar_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'proveedores_form.html', {'form': form, 'proveedor': proveedor})

def desactivar_proveedor(request, proveedor_id):
    """Desactivar un proveedor"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.activo = False
    proveedor.save()
    return redirect('listar_proveedores')

# ============================================
# 2. VIEWSETS API REST
# ============================================

class ProveedorViewSet(viewsets.ModelViewSet):
    """API REST para Proveedores"""
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    
    def list(self, request, *args, **kwargs):
        """GET /api/proveedores/ - Listar todos"""
        proveedores = Proveedor.objects.filter(activo=True)
        serializer = self.get_serializer(proveedores, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """POST /api/proveedores/ - Crear nuevo"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)