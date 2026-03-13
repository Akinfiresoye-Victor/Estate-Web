# company/urls.py
from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('form/',views.agent_form, name='agent-form'),
    path('profile/<agent_uuid>', views.agent_profile, name='agent-profile'),
    path('profile/update/<agent_uuid>',views.update_agent_profile, name='update-agent' ),
    path('lead/management', views.lead_management, name='leads'),
    path('analytics', views.analytics, name='analytics'),
    path('lead/detail/<lead_id>', views.lead_detail, name='lead-detail'),
    path('settings', views.settings, name='settings'),
    path('lead/delete/<lead_id>', views.delete_lead, name='delete-lead'),
    path('lead/update_status/<int:lead_id>/', views.agent_update_lead_status, name='agent-update-lead-status'),
    path('lead/update_stage/<int:lead_id>/', views.agent_update_lead_stage, name='agent-update-lead-stage'),
    path('jobs/listings', views.job_listings, name='job-listings'),
    path('jobs/detail/<job_id>',views.job_detail, name='job-detail'),
    path('delete/agent/<agent_uuid>', views.delete_agent, name='delete-agent')
]
