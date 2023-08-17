
from django.urls import path
from . import views


urlpatterns = [
    path('', views.store, name='store'),
    path('wishlist/', views.users_wishlist, name='wishlist'),
    path('add_to_wishlist/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('retro/', views.retro_store, name='retro'),
    path('<slug:club_slug>/', views.store, name='related_products'),
    path('product_details/<int:pid>/', views.product_details, name='product_details'),
    path('submit_review/<int:pid>/', views.submit_review, name='submit_review'),
    path('maradona', views.maradona_products, name='maradona'),

]