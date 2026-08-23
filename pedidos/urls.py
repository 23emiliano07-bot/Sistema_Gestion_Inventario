from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/pedidos', views.PedidoViewSet, basename='api_pedidos')
router.register(r'api/backorders', views.BackOrderViewSet, basename='api_backorders')

urlpatterns = [
    path('', views.listar_pedidos, name='listar_pedidos'),
    path('crear/', views.crear_pedido, name='crear_pedido'),
    path('<int:pedido_id>/editar/', views.editar_pedido, name='editar_pedido'),
    path('', include(router.urls)),
]