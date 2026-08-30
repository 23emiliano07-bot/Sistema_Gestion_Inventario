from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'email', 'telefono', 'descripcion', 'direccion', 'ciudad', 'estado', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@proveedor.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+52 1234567890'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del proveedor'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección completa'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado/Provincia'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_nombre(self):
        """Valida el nombre del proveedor"""
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres")
        return nombre.strip().title()
    
    def clean_email(self):
        """Valida el email"""
        email = self.cleaned_data.get('email')
        if email:
            # Validar formato básico
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                raise ValidationError("Ingresa un email válido.")
        return email.lower()
    
    def clean_telefono(self):
        """Valida el teléfono"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Remover espacios y caracteres especiales
            telefono_limpio = re.sub(r'\D', '', telefono)
            if len(telefono_limpio) < 10:
                raise ValidationError("El teléfono debe tener al menos 10 dígitos.")
        return telefono.strip()
    
    def clean_ciudad(self):
        """Valida la ciudad"""
        ciudad = self.cleaned_data.get('ciudad')
        if ciudad and len(ciudad) < 2:
            raise ValidationError("La ciudad debe tener al menos 2 caracteres.")
        return ciudad.strip().title() if ciudad else ciudad
    
    def clean_estado(self):
        """Valida el estado"""
        estado = self.cleaned_data.get('estado')
        if estado and len(estado) < 2:
            raise ValidationError("El estado debe tener al menos 2 caracteres.")
        return estado.strip().title() if estado else estado