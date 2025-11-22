from django.contrib import admin
from .models import *
from members.models import User
from companies.models import CompanyInformation, CompanyAnalytics
from agents.models import Experience, SocialLinks, AgentInformation
from estate.models import UserInformation, LeadInfo


#registering all our models to our admin site
admin.site.register([PropertyManagementSale, PropertyManagementRent, Feedback, AgentInformation,
                    Experience, SocialLinks, UserInformation, PropertyRentImage, PropertySaleImage, User, CompanyInformation,
                    CompanyAnalytics, PropertyManagementRentAnalytics, PropertyManagementSaleAnalytics, LeadInfo,WishlistForRent,
                    WishlistForSale
                    ])
    