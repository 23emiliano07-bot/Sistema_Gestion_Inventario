from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Pedido, DetallesPedido, BackOrder

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['numero_pedido', 'proveedor', 'estado', 'fecha_entrega', 'notas']
        widgets = {
            'numero_pedido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: FPA250726'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'}),
        }
    
    def clean_numero_pedido(self):
        """Valida el número de pedido"""
        numero_pedido = self.cleaned_data.get('numero_pedido')
        if not numero_pedido:
            raise ValidationError("El número de pedido es requerido.")
        if len(numero_pedido) < 5:
            raise ValidationError("El número de pedido debe tener al menos 5 caracteres.")
        return numero_pedido.upper().strip()
    
    def clean_fecha_entrega(self):
        """Valida que la fecha no sea en el pasado"""
        fecha_entrega = self.cleaned_data.get('fecha_entrega')
        if fecha_entrega:
            if fecha_entrega < datetime.now().date():
                raise ValidationError("La fecha de entrega no puede ser en el pasado.")
        return fecha_entrega

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