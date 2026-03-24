'''Routes that handles the logging in, logging out, and registration of users'''

from django.urls import path
from . import views

urlpatterns = [
    path('login_user', views.login_user, name='login'),
    path('logout_user', views.logout_user, name='logout'),
    path('register_customer', views.register_customer, name='register-customer'),
    
    path('register_agent', views.register_agent, name='register-agent'),
    
    path('company/register_user', views.register_company, name='register-company'),
]

