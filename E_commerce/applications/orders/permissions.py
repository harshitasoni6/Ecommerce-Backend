from rest_framework.permissions import BasePermission

class IsOrderOwnerOrSellerOrAdmin(BasePermission):
    """
    - Admin can see all orders.
    - Seller can see orders containing their products.
    - Customer can see only their own orders.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        if getattr(user, 'role', None) == 'seller':
            return any(item.product.seller == user for item in obj.items.all())
        return obj.user == user
