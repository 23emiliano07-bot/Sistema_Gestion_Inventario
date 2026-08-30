from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)

class AuditoriaMiddleware(MiddlewareMixin):
    """Middleware para registrar cambios en la aplicación"""
    
    def process_request(self, request):
        # Guardar usuario y método en la request
        request.usuario_auditoria = request.user if request.user.is_authenticated else 'Anónimo'
        request.metodo_auditoria = request.method
        request.ruta_auditoria = request.path
        return None
    
    def process_response(self, request, response):
        # Registrar cambios (POST, PUT, DELETE)
        if request.method in ['POST', 'PUT', 'DELETE']:
            usuario = getattr(request, 'usuario_auditoria', 'Desconocido')
            logger.info(f"AUDITORÍA - Usuario: {usuario} | Método: {request.method} | Ruta: {request.path} | Status: {response.status_code}")
        return response