from rest_framework import serializers
from .models import Order, OrderItem
from product.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_id', 'quantity']
        read_only_fields = ['order']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'created_at', 'updated_at', 'items',
            'full_name', 'email', 'phone', 'address', 'city', 'postal_code', 'notes'
        ]
        read_only_fields = ['created_at', 'updated_at']
