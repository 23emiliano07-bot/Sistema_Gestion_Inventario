from rest_framework import serializers
from .models import Pedido, BackOrder

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'

class BackOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackOrder
        fields = '__all__'