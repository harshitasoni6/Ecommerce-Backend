from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .permissions import IsSellerOwnerOrAdmin
from applications.users.permissions import IsSellerOrAdmin

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsSellerOrAdmin()]
        return [permissions.AllowAny()]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'seller', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsSellerOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsSellerOwnerOrAdmin()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Product.objects.filter(is_active=True)
        
        if user.role == 'admin':
            return Product.objects.all()
        elif user.role == 'seller':
            return Product.objects.filter(seller=user)
        else:  # customer
            return Product.objects.filter(is_active=True)
