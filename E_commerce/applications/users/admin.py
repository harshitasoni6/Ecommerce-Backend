from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address')}),
    )



# @admin.register(OutstandingToken)
# class OutstandingTokenAdmin(admin.ModelAdmin):
#     list_display = ['user', 'jti', 'created_at', 'expires_at']
#     list_filter = ['created_at', 'expires_at']
#     search_fields = ['user__username', 'jti']
#     readonly_fields = ['token', 'jti', 'created_at', 'expires_at']
    
#     def has_add_permission(self, request):
#         return False

# @admin.register(BlacklistedToken)
# class BlacklistedTokenAdmin(admin.ModelAdmin):
#     list_display = ['token_jti', 'blacklisted_at']
#     list_filter = ['blacklisted_at']
#     search_fields = ['token__jti', 'token__user__username']
#     readonly_fields = ['token', 'blacklisted_at']
    
#     def token_jti(self, obj):
#         return obj.token.jti
#     token_jti.short_description = 'Token JTI'
    
#     def has_add_permission(self, request):
#         return False