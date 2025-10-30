from rest_framework import serializers
from .models import Order, OrderItem
from applications.products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'seller', 'seller_name', 'quantity', 'price', 'subtotal']
        read_only_fields = ['id', 'price', 'seller']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'status', 'total_amount', 
                  'shipping_address', 'phone', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer', 'total_amount', 'created_at', 'updated_at']

class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    phone = serializers.CharField(max_length=15)

