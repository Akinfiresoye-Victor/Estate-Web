from django.urls import path
from . import views

app_name = 'landlord'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory, name='inventory'),
    path('profile_setup/', views.profile_setup, name='profile-setup'),
]