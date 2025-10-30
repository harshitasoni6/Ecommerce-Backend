from rest_framework import serializers
from .models import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'order', 'order_id', 'user', 'amount', 'payment_method', 
                  'razorpay_order_id', 'razorpay_payment_id', 'transaction_id',
                  'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'razorpay_order_id', 'transaction_id', 
                           'status', 'created_at', 'updated_at']

class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=['razorpay', 'cod'])

class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()