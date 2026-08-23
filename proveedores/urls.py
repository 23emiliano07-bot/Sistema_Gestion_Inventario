from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para API REST
router = DefaultRouter()
router.register(r'api/proveedores', views.ProveedorViewSet, basename='api_proveedores')  # ← COMENTA ESTA LÍNEA

urlpatterns = [
    # Rutas Web (HTML)
    path('', views.listar_proveedores, name='listar_proveedores'),
    path('crear/', views.crear_proveedor, name='crear_proveedor'),
    path('<int:proveedor_id>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('<int:proveedor_id>/desactivar/', views.desactivar_proveedor, name='desactivar_proveedor'),
    
    # Rutas API REST
    path('', include(router.urls)),  # ← COMENTA ESTA TAMBIÉN
]