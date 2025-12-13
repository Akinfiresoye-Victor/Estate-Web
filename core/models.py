from django.db import models
from .choices import *
import django
from .validators import validate_image
from django.utils import timezone
from members.models import User 



#model handling the datatabase requirements cointaining all the property up for sale requirements.
class PropertyManagementSale(models.Model):
    users=models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user_id=models.IntegerField('Listee Users ID', blank=False, default=1)
    company_uuid=models.CharField('Company_uuid', max_length=40, default='None', blank=True)
    agent_uuid= models.CharField('Agent_uuid', max_length=36, default='None', blank=True)
    property_description = models.TextField('Description', max_length=200,blank=True)
    location = models.CharField('Location', max_length=100)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos')
    phone_number = models.CharField('Phone Number', max_length=12, blank=False)
    price = models.DecimalField(max_digits=100,null=False, blank=False, decimal_places=2, default=0)
    bedrooms = models.IntegerField(default=0, blank=True, null=True)
    bathrooms = models.IntegerField(default=0, blank=True, null=True)
    parking_spaces=models.IntegerField(default=0, blank=True, null=True)
    size= models.IntegerField('size', blank=True, default=300)
    available= models.BooleanField('Available', default=True)
    last_updated = models.DateTimeField(auto_now=True)
    property_category=models.CharField(choices=PROPERTY_CATEGORY, default='Residential')
    residential= models.CharField(max_length=30, choices=RESIDENTIAL_PROPERTIES, default='Apartment', blank=True)
    commercial= models.CharField(max_length=30, choices=COMMERCIAL_PROPERTIES, default='Office Space', blank=True)
    lands= models.CharField(max_length=30, choices=LAND, default='Farmland', blank=True)
    base_image= models.ImageField(null=True, blank=True, upload_to="images/buy", validators=[validate_image])
    listed_date=models.DateTimeField(default=timezone.now, blank=True)
    time_stamp=models.DateTimeField(null=True,blank=True, default=timezone.now)
    last_reset_date= models.DateTimeField(default=timezone.now)
    property_type=models.CharField('property Type', default='Sale')
    total_likes=models.IntegerField('Wishlisted time', default=0, blank=False, null=False)


class PropertyManagementSaleAnalytics(models.Model):
    on_sale= models.ForeignKey(PropertyManagementSale, on_delete=models.CASCADE, related_name='prop_analytics')
    session_id= models.IntegerField('user_id', default=None)
    inquires_check=models.IntegerField('Inquiries', default=None)




#model handling the datatabase requirements cointaining all the property up for lease requirements
class PropertyManagementRent(models.Model):
    users=models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user_id=models.IntegerField('Landlord', blank=False, default=1)
    company_uuid=models.CharField('Company', max_length=36, default='None', blank=True)
    agent_uuid= models.CharField('Agent', max_length=36, default='None', blank=True)
    description= models.TextField('Description',max_length=200, blank=True )
    location= models.CharField('Location', max_length=100, blank=False)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos State')
    phone_number = models.CharField('Phone Number', max_length=12)
    price_range = models.DecimalField(max_digits=100, blank=False, decimal_places=2, default=0)
    available=models.BooleanField('Availble', default=True)
    bedrooms = models.IntegerField(default=0, blank=True, null=True)
    bathrooms = models.IntegerField(default=0, blank=True, null=True)
    size= models.IntegerField('size', blank=True, default=0)
    parking_spaces=models.IntegerField(default=0, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    property_category=models.CharField(choices=PROPERTY_CATEGORY,default='Residential')
    residential= models.CharField(max_length=30, choices=RESIDENTIAL_PROPERTIES, default='Apartment', blank=True)
    commercial= models.CharField(max_length=30, choices=COMMERCIAL_PROPERTIES, default='Office Space', blank=True)
    lands= models.CharField(max_length=30, choices=LAND, default='Farmland', blank=True)
    base_image= models.ImageField(null=True, blank=True, upload_to="images/rent", validators=[validate_image])
    listed_date=models.DateTimeField(default=timezone.now, blank=True)
    time_stamp=models.DateTimeField(null=True,blank=True, default=timezone.now)
    last_reset_date= models.DateTimeField(default=timezone.now)
    property_type=models.CharField('property Type', default='Rent')
    total_likes=models.IntegerField('Wishlisted time', default=0, blank=False, null=False)


class PropertyManagementRentAnalytics(models.Model):
    on_lease= models.ForeignKey(PropertyManagementRent, on_delete=models.CASCADE, related_name='prop_analytics')
    session_id= models.IntegerField('user_id', default=None)
    inquires_check=models.IntegerField('Inquiries', default=None)




'''Image Handling'''
class PropertySaleImage(models.Model):
    property= models.ForeignKey(PropertyManagementSale, on_delete=models.CASCADE, related_name='images')
    more_images= models.ImageField(null=True, blank=True, upload_to="images/buy", validators=[validate_image])
    caption=models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"{self.property} - image {self.pk}"

class PropertyRentImage(models.Model):
    property=models.ForeignKey(PropertyManagementRent, on_delete=models.CASCADE, related_name='images')
    more_images= models.ImageField(null=True, blank=True, upload_to="images/rent", validators=[validate_image])
    caption=models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"{self.property} - image {self.pk}"



class Feedback(models.Model):
    email=models.EmailField('Your Email')
    feedback= models.CharField(max_length=300, blank=False)
    date_sent= models.DateField(default=django.utils.timezone.now)



class WishlistStorageUnit(models.Model):
    user_id=models.IntegerField('Owner Of Wishlist', default=1, null=False, blank=False)
    property_id=models.IntegerField('Property In Question', default=1,null=False, blank=False)
    property_type=models.CharField('Property_type', default='Rent', null=False, blank=False)