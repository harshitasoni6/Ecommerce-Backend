from rest_framework import permissions

class IsSellerOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'seller':
            return obj.seller == request.user
        return False