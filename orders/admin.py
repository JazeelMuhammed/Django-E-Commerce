from django.contrib import admin
from .models import Payment, Order, ProductOrdered

# Register your models here.


class ProductOrderedInline(admin.TabularInline):
    model = ProductOrdered
    extra = 0
    readonly_fields = ['payment', 'user', 'product', 'variation', 'qty', 'price', 'ordered']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'fullname', 'phone', 'email', 'city', 'total', 'tax', 'order_status', 'is_ordered', 'ordered_at']
    list_filter = ['order_status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone']
    inlines = [ProductOrderedInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductOrdered)