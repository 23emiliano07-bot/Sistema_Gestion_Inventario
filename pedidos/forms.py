from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Pedido, DetallesPedido, BackOrder, Almacen

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['numero_pedido', 'proveedor', 'estado', 'orden_compra', 'orden_venta', 'responsable', 'notas']
        widgets = {
            'numero_pedido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: FPA250726'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'orden_compra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: OC-2026-001'}),
            'orden_venta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: OV-2026-001'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si es un nuevo pedido (no tiene pk), mostrar solo "Pendiente"
        if not self.instance.pk:
            self.fields['estado'].choices = [
                choice for choice in self.fields['estado'].choices 
                if choice[0] == 'pendiente'
            ] 
    
        # Si es edición, aplicar lógica de estados progresivos
        elif self.instance.pk:
            estado_actual = self.instance.estado
        
            estados_validos = {
                'pendiente': ['pendiente', 'confirmado'],
                'confirmado': ['confirmado', 'solicitado'],
                'solicitado': ['solicitado', 'entregado'],
                'entregado': ['entregado'],
            }
        
            opciones_validas = estados_validos.get(estado_actual, [])
            self.fields['estado'].choices = [
                choice for choice in self.fields['estado'].choices 
                if choice[0] in opciones_validas
        ]
    
    
    def clean_numero_pedido(self):
        """Valida el número de pedido"""
        numero_pedido = self.cleaned_data.get('numero_pedido')
        if not numero_pedido:
            raise ValidationError("El número de pedido es requerido.")
        if len(numero_pedido) < 5:
            raise ValidationError("El número de pedido debe tener al menos 5 caracteres.")
        return numero_pedido.upper().strip()
    
class DetallesPedidoForm(forms.ModelForm):
    class Meta:
        model = DetallesPedido
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio unitario', 'step': '0.01', 'min': '0'}),
        }
    
    def clean_cantidad(self):
        """Valida que la cantidad sea positiva"""
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad and cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad
    
    def clean_precio_unitario(self):
        """Valida que el precio sea positivo"""
        precio_unitario = self.cleaned_data.get('precio_unitario')
        if precio_unitario and precio_unitario <= 0:
            raise ValidationError("El precio unitario debe ser mayor a cero.")
        return precio_unitario

class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'descripcion', 'ubicacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Almacén Central'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción (opcional)'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Temixco, Morelos'}),
        }
    
    def clean_nombre(self):
        """Valida el nombre del almacén"""
        nombre = self.cleaned_data.get('nombre')
        if not nombre:
            raise ValidationError("El nombre del almacén es requerido.")
        return nombre.strip()