from django.contrib import admin
from .models import Cart, CartProduct

# Register your models here.


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added',)


class CartProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'qty', 'is_active',)


admin.site.register(Cart, CartAdmin)
admin.site.register(CartProduct, CartProductAdmin)
