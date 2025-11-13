# company/urls.py
from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]
