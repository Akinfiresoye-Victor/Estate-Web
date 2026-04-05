from django.urls import path
from . import views

app_name = 'control_panel'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.users, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/suspend/', views.suspend_user, name='suspend_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('agents/', views.agents, name='agents'),
    path('agents/<str:agent_uuid>/', views.agent_detail, name='agent_detail'),
    path('agents/<str:agent_uuid>/verify/', views.toggle_agent_verified, name='toggle_agent_verified'),
    path('companies/', views.companies, name='companies'),
    path('companies/<str:company_id>/', views.company_detail, name='company_detail'),
    path('companies/<str:company_id>/verify/', views.toggle_company_verified, name='toggle_company_verified'),
    path('companies/<str:company_id>/tier/', views.change_company_tier, name='change_company_tier'),
    path('listings/', views.listings, name='listings'),
    path('listings/<str:type>/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listings/<str:type>/<int:pk>/unlist/', views.force_unlist, name='force_unlist'),
    path('listings/<str:type>/<int:pk>/feature/', views.toggle_feature, name='toggle_feature'),
    path('listings/<str:type>/<int:pk>/flag/', views.toggle_flag, name='toggle_flag'),
    path('listings/<str:type>/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('access-log/', views.access_log, name='access_log'),
]

