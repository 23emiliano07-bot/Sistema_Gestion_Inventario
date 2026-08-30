from django import forms
from .models import Pedido, DetallesPedido, BackOrder

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['numero_pedido', 'proveedor', 'estado', 'fecha_entrega', 'notas']
        widgets = {
            'numero_pedido': forms.TextInput(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DetallesPedidoForm(forms.ModelForm):
    class Meta:
        model = DetallesPedido
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
        }