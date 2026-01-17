# company/urls.py
from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('form/',views.agent_form, name='agent-form'),
    path('profile/<agent_uuid>', views.agent_profile, name='agent-profile'),
    path('lead/management', views.lead_management, name='leads'),
    path('analytics', views.analytics, name='analytics'),
    path('lead/detail/<lead_id>', views.lead_detail, name='lead-detail'),
    path('settings', views.settings, name='settings'),
    path('lead/delete/<lead_id>', views.delete_lead, name='delete-lead')
]
