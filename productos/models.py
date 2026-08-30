from django.db import models
from django.core.exceptions import ValidationError

def validar_precio_positivo(value):
    """Valida que el precio sea mayor a cero"""
    if value <= 0:
        raise ValidationError('El precio debe ser un número mayor a cero.')

class Producto(models.Model):
    """Modelo para gestionar Productos"""
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[validar_precio_positivo]  # ← VALIDACIÓN AGREGADA
    )
    categoria = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(default=0)
    disponible = models.BooleanField(default=True)
    
    # Multimedia (imagen)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)  # ← AGREGADO
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return self.nombre