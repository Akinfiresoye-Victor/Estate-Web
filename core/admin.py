from django.contrib import admin
from .models import *
from members.models import User
from companies.models import CompanyInformation, CompanyAnalytics, SessionId
from agents.models import Experience, SocialLinks, AgentInformation
from estate.models import LeadInfo


#registering all our models to our admin site
admin.site.register([PropertyManagementSale, PropertyManagementRent, Feedback, AgentInformation,
                    Experience, SocialLinks, PropertyRentImage, PropertySaleImage, User, CompanyInformation,
                    CompanyAnalytics, LeadInfo,WishlistStorageUnit, SessionId, PropertyViews,Appointments
                    ])