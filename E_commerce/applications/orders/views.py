from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.http import HttpResponse
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from applications.cart.models import Cart
from applications.common.utils import generate_invoice_pdf

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            return Order.objects.all()
        elif user.role == 'seller':
            return Order.objects.filter(items__seller=user).distinct()
        else:  # customer
            return Order.objects.filter(customer=user)
    
    @transaction.atomic
    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check stock availability
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response(
                    {"error": f"Insufficient stock for {item.product.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create order
        order = Order.objects.create(
            customer=request.user,
            total_amount=cart.total_amount,
            shipping_address=serializer.validated_data['shipping_address'],
            phone=serializer.validated_data['phone']
        )
        
        # Create order items and update stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                seller=item.product.seller,
                quantity=item.quantity,
                price=item.product.price
            )
            
            # Decrease stock
            item.product.stock -= item.quantity
            item.product.save()
        
        # Clear cart
        cart.items.all().delete()
        
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        
        # Only admin and seller (for their products) can update status
        if request.user.role == 'customer':
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.role == 'seller':
            # Check if seller owns any product in this order
            if not order.items.filter(seller=request.user).exists():
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        order = self.get_object()
        
        # Generate PDF invoice
        pdf = generate_invoice_pdf(order)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        return response
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.customer != request.user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status in ['shipped', 'delivered']:
            return Response(
                {"error": "Cannot cancel order that has been shipped or delivered"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Restore stock
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
        
        order.status = 'cancelled'
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)


