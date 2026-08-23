from usuarios.models import Usuario

class UsuarioDAO:
    @staticmethod
    def obtener_todos():
        return Usuario.objects.all()
    
    @staticmethod
    def obtener_por_id(usuario_id):
        try:
            return Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return None