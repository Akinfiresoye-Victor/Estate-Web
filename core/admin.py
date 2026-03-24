from django.contrib import admin
from .models import *
from members.models import User
from companies.models import *
from agents.models import Experience, SocialLinks, AgentInformation, AgentAnalytics
from agents.models import SessionId as agent_session
from estate.models import LeadInfo


#registering all our models to our admin site
admin.site.register([PropertyManagementSale, PropertyManagementRent, Feedbacks, AgentInformation,
                    Experience, SocialLinks, PropertyRentImage, PropertySaleImage, User, CompanyInformation,
                    CompanyAnalytics, LeadInfo,WishlistStorageUnit, SessionId, PropertyViews,Appointments, 
                    AgentAnalytics, agent_session, CompanyRating,JobPost, CompanyActivityLog,Employees, InviteLink,
                    Partnership,PartnershipGoal,ErrorLog
                    ])

