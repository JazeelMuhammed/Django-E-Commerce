from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    # Password Reset
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('validate_reset_password/<uidb64>/<token>/', views.validate_reset_password, name='validate_reset_password'),
    path('reset-password/', views.reset_password, name='reset-password'),

    # Change Password
    path('change_password/', views.change_password, name='change_password'),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)