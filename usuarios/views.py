from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from .models import Usuario
from .serializers import UsuarioSerializer
from .forms import UsuarioForm

@login_required(login_url='admin:login')
@permission_required('usuarios.view_usuario', raise_exception=True)
def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})

@login_required(login_url='admin:login')
@permission_required('usuarios.add_usuario', raise_exception=True)
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios_form.html', {'form': form})

@login_required(login_url='admin:login')
@permission_required('usuarios.change_usuario', raise_exception=True)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios_form.html', {'form': form, 'usuario': usuario})

@login_required(login_url='admin:login')
@permission_required('usuarios.delete_usuario', raise_exception=True)
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    usuario.delete()
    return redirect('listar_usuarios')

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]