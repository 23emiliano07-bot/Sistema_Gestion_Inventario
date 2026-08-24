from ..models import Proveedor

class ProveedorDAO:
    """
    Data Access Object para gestionar Proveedores
    """
    
    @staticmethod
    def crear_proveedor(nombre, email, telefono=None, descripcion=None, direccion=None, ciudad=None, estado=None):
        """Crear un nuevo proveedor"""
        try:
            proveedor = Proveedor.objects.create(
                nombre=nombre,
                email=email,
                telefono=telefono,
                descripcion=descripcion,
                direccion=direccion,
                ciudad=ciudad,
                estado=estado
            )
            return proveedor
        except Exception as e:
            print(f"Error al crear proveedor: {e}")
            return None
    
    @staticmethod
    def obtener_proveedor(proveedor_id):
        """Obtener un proveedor por ID"""
        try:
            return Proveedor.objects.get(id=proveedor_id)
        except Proveedor.DoesNotExist:
            return None
    
    @staticmethod
    def obtener_todos_proveedores():
        """Obtener todos los proveedores activos"""
        return Proveedor.objects.filter(activo=True).order_by('nombre')
    
    @staticmethod
    def actualizar_proveedor(proveedor_id, **kwargs):
        """Actualizar un proveedor"""
        try:
            proveedor = Proveedor.objects.get(id=proveedor_id)
            for key, value in kwargs.items():
                if hasattr(proveedor, key):
                    setattr(proveedor, key, value)
            proveedor.save()
            return proveedor
        except Proveedor.DoesNotExist:
            return None
    
    @staticmethod
    def desactivar_proveedor(proveedor_id):
        """Desactivar un proveedor (soft delete)"""
        try:
            proveedor = Proveedor.objects.get(id=proveedor_id)
            proveedor.activo = False
            proveedor.save()
            return proveedor
        except Proveedor.DoesNotExist:
            return None
    
    @staticmethod
    def buscar_proveedor(criterio):
        """Buscar proveedores por nombre o email"""
        return Proveedor.objects.filter(
            activo=True,
            nombre__icontains=criterio
        ) | Proveedor.objects.filter(
            activo=True,
            email__icontains=criterio
        )