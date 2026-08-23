from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets

from .models import Usuario
from .serializers import UsuarioSerializer
from .forms import UsuarioForm

def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar.html', {'usuarios': usuarios})

def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear.html', {'form': form})

def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar.html', {'form': form, 'usuario': usuario})

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer