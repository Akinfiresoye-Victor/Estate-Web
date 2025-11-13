from django.contrib import admin
from .models import *
from members.models import User
from companies.models import CompanyInformation, CompanyAnalytics

#registering all our models to our admin site
admin.site.register([PropertyManagementSale, PropertyManagementRent, Feedback, Agent_Information,
                    Experience, SocialLinks, UserInformation, PropertyRentImage, PropertySaleImage, User, CompanyInformation,
                    CompanyAnalytics, PropertyManagementRentAnalytics, PropertyManagementSaleAnalytics, LeadInfo, 
                    LeadStatus])
