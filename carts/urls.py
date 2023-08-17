from django.urls import path
from . import views


urlpatterns = [
    path('shopping_cart/', views.cart, name='shopping-cart'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('decrement_cart/<int:pk>/<int:cart_product_id>/', views.decrement_cart, name='decrement_cart'),
    path('remove_cart_product/<int:pk>/<int:cart_product_id>/', views.remove_cart_product, name='remove_cart_product'),
    path('checkout/', views.checkout, name='checkout'),
    path('wishlist/', views.cart, name='wishlist'),
    path('add_to_wishlist/<int:pk>/', views.add_to_cart, name='add_to_wishlist'),
]