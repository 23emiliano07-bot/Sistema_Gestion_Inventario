from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from productos.models import Producto
from proveedores.models import Proveedor

class Almacen(models.Model):
    """Almacenes que pueden hacer pedidos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Almacenes"
    
    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('solicitado', 'Solicitado'),
        ('entregado', 'Entregado'),
    ]
    
    numero_pedido = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='pedidos')
    estado = models.CharField(max_length=50, choices=ESTADOS, default='pendiente')
    fecha_pedido = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True, null=True)
    orden_compra = models.CharField(max_length=100, blank=True, null=True)
    orden_venta = models.CharField(max_length=100, blank=True, null=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_solicitados')
    
    class Meta:
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"{self.numero_pedido} - {self.proveedor.nombre}"
    
    @property
    def total(self):
        """Calcula el total sumando todos los detalles"""
        return sum(detalle.subtotal for detalle in self.detalles.all())

class DetallesPedido(models.Model):
    """Relación entre Pedido, Producto y Almacén"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    recibido = models.IntegerField(default=0)
    pendiente = models.IntegerField(default=0)
    folio_factura = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Detalles de Pedidos"
        unique_together = ('pedido', 'producto', 'almacen')
    
    def clean(self):
        """Valida que no haya productos duplicados por almacén"""
        duplicado = DetallesPedido.objects.filter(
            pedido=self.pedido,
            producto=self.producto,
            almacen=self.almacen
        ).exclude(pk=self.pk)
        
        if duplicado.exists():
            raise ValidationError(
                f"❌ El producto '{self.producto.nombre}' ya está en este pedido para el almacén '{self.almacen.nombre}'. "
                "Actualiza la cantidad en su lugar."
            )
    
    @property
    def subtotal(self):
        """Calcula el subtotal de este detalle"""
        return self.cantidad * self.precio_unitario
    
    def __str__(self):
        return f"{self.pedido.numero_pedido} - {self.producto.nombre} - {self.almacen.nombre if self.almacen else 'Sin almacén'}"

class BackOrder(models.Model):
    """Para productos pendientes (cantidades faltantes)"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='backorders')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, null=True, blank=True)
    orden_compra = models.CharField(max_length=100, blank=True, null=True)
    cantidad = models.IntegerField()
    entregado = models.IntegerField(default=0)
    resuelto = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Back Orders"
    
    def __str__(self):
        return f"BO - {self.pedido.numero_pedido} - {self.producto.nombre}"