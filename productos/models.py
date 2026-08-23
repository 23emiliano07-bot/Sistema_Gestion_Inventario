from django.db import models

class Producto(models.Model):
    """Modelo para gestionar Productos"""
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(default=0)
    disponible = models.BooleanField(default=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return self.nombre