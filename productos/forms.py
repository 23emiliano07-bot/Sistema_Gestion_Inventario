from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock', 'categoria', 'descripcion', 'disponible', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 99.99', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad disponible', 'min': '0'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del producto'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def clean_precio(self):
        """Valida que el precio sea mayor a cero"""
        precio = self.cleaned_data.get('precio')
        if precio and precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a cero.')
        return precio
    
    def clean_stock(self):
        """Valida que el stock sea no negativo"""
        stock = self.cleaned_data.get('stock')
        if stock and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock
    
    def clean_nombre(self):
        """Valida el nombre del producto"""
        nombre = self.cleaned_data.get('nombre')
        if nombre and len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre
    

    def clean_imagen(self):
         """Valida el archivo de imagen"""
         imagen = self.cleaned_data.get('imagen')
         if imagen:
             # Validar tamaño (máximo 5MB)
             if imagen.size > 5 * 1024 * 1024:
                 raise forms.ValidationError('La imagen no debe exceder 5MB.')
        
             # Validar formato por extensión
             extensiones_permitidas = ['jpg', 'jpeg', 'png', 'gif', 'webp']
             ext = imagen.name.split('.')[-1].lower()
             if ext not in extensiones_permitidas:
                raise forms.ValidationError('Solo se permiten imágenes JPG, PNG, GIF o WEBP.')
         return imagen