from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'rol', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }