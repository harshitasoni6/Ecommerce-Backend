from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import razorpay
import hmac
import hashlib
from .models import PaymentTransaction
from .serializers import (
    PaymentTransactionSerializer, 
    CreatePaymentSerializer, 
    VerifyPaymentSerializer
)
from applications.orders.models import Order

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return PaymentTransaction.objects.all()
        return PaymentTransaction.objects.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """
        Create a Razorpay order and payment transaction
        """
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        payment_method = serializer.validated_data['payment_method']
        
        try:
            order = Order.objects.get(id=order_id, customer=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if payment already exists
        if hasattr(order, 'payment'):
            return Response(
                {"error": "Payment already exists for this order"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle Cash on Delivery
        if payment_method == 'cod':
            payment = PaymentTransaction.objects.create(
                order=order,
                user=request.user,
                amount=order.total_amount,
                payment_method=payment_method,
                transaction_id=f"COD_{order.id}_{request.user.id}",
                status='pending'
            )
            
            return Response({
                'payment_id': payment.id,
                'message': 'Cash on Delivery order placed successfully',
                'payment_method': 'cod'
            }, status=status.HTTP_201_CREATED)
        
        # Handle Razorpay payment
        try:
            # Convert amount to paise (1 INR = 100 paise)
            amount_in_paise = int(order.total_amount * 100)
            
            # Create Razorpay order
            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1,  # Auto capture
                'notes': {
                    'order_id': order.id,
                    'customer_email': request.user.email
                }
            })
            
            # Create payment transaction
            payment = PaymentTransaction.objects.create(
                order=order,
                user=request.user,
                amount=order.total_amount,
                payment_method=payment_method,
                razorpay_order_id=razorpay_order['id'],
                transaction_id=razorpay_order['id'],
                status='pending'
            )
            
            return Response({
                'payment_id': payment.id,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': amount_in_paise,
                'currency': 'INR',
                'name': 'E-Commerce Store',
                'description': f'Order #{order.id}',
                'prefill': {
                    'name': request.user.get_full_name() or request.user.username,
                    'email': request.user.email,
                    'contact': order.phone
                }
            }, status=status.HTTP_201_CREATED)
            
        except razorpay.errors.BadRequestError as e:
            return Response(
                {"error": f"Razorpay error: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error creating payment: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        """
        Verify Razorpay payment signature
        """
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        razorpay_order_id = serializer.validated_data['razorpay_order_id']
        razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
        razorpay_signature = serializer.validated_data['razorpay_signature']
        
        try:
            # Get payment transaction
            payment = PaymentTransaction.objects.get(
                razorpay_order_id=razorpay_order_id,
                user=request.user
            )
        except PaymentTransaction.DoesNotExist:
            return Response(
                {"error": "Payment transaction not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify signature
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature == razorpay_signature:
            # Payment verified successfully
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'completed'
            payment.save()
            
            # Update order status
            payment.order.status = 'processing'
            payment.order.save()
            
            return Response({
                'message': 'Payment verified successfully',
                'payment_id': payment.id,
                'status': 'completed'
            }, status=status.HTTP_200_OK)
        else:
            payment.status = 'failed'
            payment.save()
            
            return Response(
                {"error": "Payment verification failed"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def payment_details(self, request, pk=None):
        """
        Get payment details from Razorpay
        """
        payment = self.get_object()
        
        if payment.payment_method == 'cod':
            return Response({
                'payment_method': 'Cash on Delivery',
                'status': payment.status,
                'amount': payment.amount
            })
        
        if not payment.razorpay_payment_id:
            return Response(
                {"error": "No payment ID found"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment_details = razorpay_client.payment.fetch(payment.razorpay_payment_id)
            return Response(payment_details, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """
        Process refund for a payment (Admin only)
        """
        payment = self.get_object()
        
        # Only admin can process refunds
        if request.user.role != 'admin':
            return Response(
                {"error": "Permission denied"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if payment.status != 'completed':
            return Response(
                {"error": "Can only refund completed payments"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cannot refund COD
        if payment.payment_method == 'cod':
            return Response(
                {"error": "Cannot refund Cash on Delivery orders online"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get refund amount from request or full amount
            refund_amount = request.data.get('amount')
            if refund_amount:
                refund_amount = int(float(refund_amount) * 100)  # Convert to paise
            else:
                refund_amount = int(payment.amount * 100)  # Full refund
            
            # Create refund
            refund = razorpay_client.payment.refund(
                payment.razorpay_payment_id,
                {
                    'amount': refund_amount,
                    'speed': 'normal',
                    'notes': {
                        'reason': request.data.get('reason', 'Customer request')
                    }
                }
            )
            
            payment.status = 'refunded'
            payment.save()
            
            return Response({
                'message': 'Refund processed successfully',
                'refund_id': refund['id'],
                'amount': refund_amount / 100
            }, status=status.HTTP_200_OK)
            
        except razorpay.errors.BadRequestError as e:
            return Response(
                {"error": f"Razorpay error: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """
        Handle Razorpay webhooks for payment events
        """
        # Verify webhook signature
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = settings.RAZORPAY_KEY_SECRET
        
        try:
            razorpay_client.utility.verify_webhook_signature(
                request.body.decode('utf-8'),
                webhook_signature,
                webhook_secret
            )
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Invalid signature"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process webhook event
        event = request.data.get('event')
        payload = request.data.get('payload', {})
        payment_entity = payload.get('payment', {}).get('entity', {})
        
        if event == 'payment.captured':
            # Payment successful
            razorpay_payment_id = payment_entity.get('id')
            razorpay_order_id = payment_entity.get('order_id')
            
            try:
                payment = PaymentTransaction.objects.get(razorpay_order_id=razorpay_order_id)
                payment.razorpay_payment_id = razorpay_payment_id
                payment.status = 'completed'
                payment.save()
                
                payment.order.status = 'processing'
                payment.order.save()
            except PaymentTransaction.DoesNotExist:
                pass
        
        elif event == 'payment.failed':
            # Payment failed
            razorpay_order_id = payment_entity.get('order_id')
            try:
                payment = PaymentTransaction.objects.get(razorpay_order_id=razorpay_order_id)
                payment.status = 'failed'
                payment.save()
            except PaymentTransaction.DoesNotExist:
                pass
        
        return Response({"status": "ok"}, status=status.HTTP_200_OK)