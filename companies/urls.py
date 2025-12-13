
from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/fill', views.company_form, name='company_form'),
    path('profile/edit/<company_id>',views.update_company_profile, name='edit-profile'),
    path('listings', views.manaage_listings, name='listings'),
    path('profile/view/<company_uuid>', views.company_profile, name='company_profile'),
    path('properties/<company_uuid>', views.properties_by_company, name='company-properties'),
    path('monthly/analytics', views.company_analytics, name='analytics'),
    path('lead/management', views.lead_management, name='lead-management'),
    path('lead/appointments', views.appointment, name='appointment'),
    path('documents/storage', views.documents, name='documents'),
    path('settings', views.company_settings, name='company-settings'),
    path('lead/delete/<lead_id>', views.delete_lead, name='delete-lead'),
    path('lead/detail/<lead_id>', views.lead_detail, name='lead-detail'),
    path('lead/update/<int:lead_id>', views.update_lead_status, name='update-lead-status'),
    path('lead/update_stage/<int:lead_id>', views.update_lead_stage, name='update-lead-stage'),
]
