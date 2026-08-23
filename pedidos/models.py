from django.db import models
from productos.models import Producto
from proveedores.models import Proveedor

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    numero_pedido = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='pendiente')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"{self.numero_pedido} - {self.proveedor.nombre}"

class BackOrder(models.Model):
    """Para productos pendientes"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cantidad_pendiente = models.IntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    resuelto = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Back Order - {self.pedido.numero_pedido}"