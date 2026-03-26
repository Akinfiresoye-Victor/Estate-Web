from django.urls import path
from . import views

app_name='executive'

urlpatterns = [
    path('overview', views.admin_dashboard, name='admin-dashboard'),
    path('verify_company/<str:company_uuid>', views.company_verification, name='verify-company'),
    path('verify_agent/<str:agent_uuid>', views.agent_verification, name='verify-agent'),
]

