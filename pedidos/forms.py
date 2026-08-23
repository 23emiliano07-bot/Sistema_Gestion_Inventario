from django import forms
from .models import Pedido, BackOrder

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['numero_pedido', 'proveedor', 'producto', 'cantidad', 'precio_unitario', 'total', 'estado', 'fecha_entrega', 'notas']
        widgets = {
            'numero_pedido': forms.TextInput(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }