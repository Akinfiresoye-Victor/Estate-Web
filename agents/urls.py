# company/urls.py
from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('form/',views.agent_form, name='agent-form'),
    path('profile/<agent_uuid>', views.agent_profile, name='agent-profile'),
]
