from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import listar_almacenes, crear_almacen, editar_almacen, eliminar_almacen

router = DefaultRouter()
router.register(r'api/pedidos', views.PedidoViewSet, basename='api_pedidos')
router.register(r'api/backorders', views.BackOrderViewSet, basename='api_backorders')

urlpatterns = [
    path('', views.listar_pedidos, name='listar_pedidos'),
    path('crear/', views.crear_pedido, name='crear_pedido'),
    path('<int:pedido_id>/editar/', views.editar_pedido, name='editar_pedido'),
    path('', include(router.urls)),
    path('<int:pedido_id>/eliminar/', views.eliminar_pedido, name='eliminar_pedido'),
    path('almacenes/', listar_almacenes, name='listar_almacenes'),
    path('almacenes/crear/', crear_almacen, name='crear_almacen'),
    path('almacenes/<int:almacen_id>/editar/', editar_almacen, name='editar_almacen'),
    path('almacenes/<int:almacen_id>/eliminar/', eliminar_almacen, name='eliminar_almacen'),
]