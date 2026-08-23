from pedidos.models import Pedido, BackOrder

class PedidoDAO:
    @staticmethod
    def obtener_todos():
        return Pedido.objects.all()
    
    @staticmethod
    def obtener_por_id(pedido_id):
        try:
            return Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            return None