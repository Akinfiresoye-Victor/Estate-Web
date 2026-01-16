from django.contrib import admin
from .models import *
from members.models import User
from companies.models import CompanyInformation, CompanyAnalytics, SessionId, CompanyRating
from agents.models import Experience, SocialLinks, AgentInformation, AgentAnalytics
from agents.models import SessionId as agent_session
from estate.models import LeadInfo
#TODOSchedule appointemnt detail - Add client information 
#TODO Add edit appointment
#TODO Cross check all authentication side to affect loss of data 

#registering all our models to our admin site
admin.site.register([PropertyManagementSale, PropertyManagementRent, Feedback, AgentInformation,
                    Experience, SocialLinks, PropertyRentImage, PropertySaleImage, User, CompanyInformation,
                    CompanyAnalytics, LeadInfo,WishlistStorageUnit, SessionId, PropertyViews,Appointments, 
                    AgentAnalytics, agent_session, CompanyRating
                    ])