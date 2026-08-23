from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/productos', views.ProductoViewSet, basename='api_productos')

urlpatterns = [
    path('', views.listar_productos, name='listar_productos'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('<int:producto_id>/desactivar/', views.desactivar_producto, name='desactivar_producto'),
    path('', include(router.urls)),
]