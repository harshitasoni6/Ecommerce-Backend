from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'seller', 'quantity', 'price', 'subtotal']
    
    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'customer__email']
    readonly_fields = ['customer', 'total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]