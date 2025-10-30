from django.db import models
from django.contrib.auth import get_user_model
from applications.orders.models import Order

User = get_user_model()

class PaymentTransaction(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD = [
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery'),  # Added COD option
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    
    # Razorpay specific fields
    razorpay_order_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)
    
    transaction_id = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order.id}"
    
    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']