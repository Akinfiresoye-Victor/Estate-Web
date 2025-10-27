from django.contrib import admin


from .models import * 


#registering all our models to our admin site
admin.site.register([PropertyManagementSale, PropertyManagementRent,Room, Messages, Feedback, Agent_Information,
                    Experience, SocialLinks, UserInformation, PropertyRentImage, PropertySaleImage])
