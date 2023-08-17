from django.contrib import admin
from .models import Product, ProductImage, Variation, ProductReview
import admin_thumbnails

# Register your models here.


@admin_thumbnails.thumbnail('images')
class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'actual_price', 'discount_price', 'stock', 'club', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductImageInline]
    search_fields = ['product_name', 'slug', 'id', 'type']


class ProductImageAdmin(admin.ModelAdmin):
    pass


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'is_active',)
    list_editable = ('is_active',)
    list_filter = ('product', 'size',)


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'subject',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)