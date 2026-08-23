from .models import Producto

class ProductoDAO:
    """DAO para Productos"""
    
    @staticmethod
    def obtener_todos():
        return Producto.objects.all()
    
    @staticmethod
    def obtener_disponibles():
        return Producto.objects.filter(disponible=True)
    
    @staticmethod
    def obtener_por_id(producto_id):
        try:
            return Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return None
    
    @staticmethod
    def crear_producto(nombre, precio, stock=0, **kwargs):
        return Producto.objects.create(
            nombre=nombre,
            precio=precio,
            stock=stock,
            **kwargs
        )
    
    @staticmethod
    def actualizar_producto(producto_id, **kwargs):
        try:
            producto = Producto.objects.get(id=producto_id)
            for key, value in kwargs.items():
                if hasattr(producto, key):
                    setattr(producto, key, value)
            producto.save()
            return producto
        except Producto.DoesNotExist:
            return None
    
    @staticmethod
    def desactivar_producto(producto_id):
        try:
            producto = Producto.objects.get(id=producto_id)
            producto.disponible = False
            producto.save()
            return producto
        except Producto.DoesNotExist:
            return None