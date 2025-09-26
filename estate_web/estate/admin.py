from django.contrib import admin


from .models import PropertyManagementSale, PropertyManagementRent


#registering all our models to our admin site
admin.site.register([PropertyManagementSale, PropertyManagementRent])
