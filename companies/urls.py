
from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/fill', views.company_form, name='company_form'),
    path('profile/edit',views.update_company_profile, name='edit-profile'),
    path('properties/<company_uuid>', views.properties_by_company, name='company-properties'),
    path('monthly/analytics', views.company_analytics, name='analytics'),
    path('lead/management', views.lead_management, name='lead-management'),
    path('documents/storage', views.documents, name='documents'),
    path('settings', views.company_settings, name='company-settings'),
    path('lead/delete/<lead_id>', views.delete_lead, name='delete-lead'),
    path('lead/detail/<lead_id>', views.lead_detail, name='lead-detail'),
    path('lead/update/<int:lead_id>', views.update_lead_status, name='update-lead-status'),
    path('lead/update_stage/<int:lead_id>', views.update_lead_stage, name='update-lead-stage'),
    path('find_talents', views.find_talents, name='find-talents'),
    path('application/management', views.manage_applications, name='application-management'),
    path('list_vacancy', views.vacancy_form, name='vacancy-form'),
    path('employee/management', views.manage_company, name='manage-company'),
    path('delete/company', views.delete_company, name='delete-company'),
    path('employee/onboard_agent/<agent_uuid>', views.onboard_agent, name='onboarding'),
    path('invite/generate/', views.generate_invite_link, name='generate_invite_link'),
    path('revoke_invite/<token>', views.revoke_invite_link, name='revoke-link'),
    path('remove_agent/<agent_uuid>', views.remove_agent, name='remove-agent'),
    path('employee/edit/<str:agent_uuid>', views.edit_employee, name='edit-employee')
]

