from django.db import models

class Usuario(models.Model):
    ROLES = [
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('almacen', 'Almacén'),
    ]
    
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.CharField(max_length=50, choices=ROLES, default='almacen')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.rol})"