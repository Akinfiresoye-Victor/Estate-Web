'''Routes that handles the logging in, logging out, and registration of users'''

from django.urls import path
from . import views

urlpatterns = [
    path('login_user', views.login_user, name='login'),
    path('logout_user', views.logout_user, name='logout'),
    path('register_customer', views.register_customer, name='register-customer'),
    path('register_agent', views.register_agent, name='register-agent'),
    path('register_landlord', views.register_landlord, name='register-landlord'),
    path('company/register_user', views.register_company, name='register-company'),
    path('google/agent/', views.agent_google_login, name='agent_google_login'),
    path('google/company/', views.company_google_login, name='company_google_login'),
    path('google/landlord/', views.landlord_google_login, name='landlord_google_login'),
]

