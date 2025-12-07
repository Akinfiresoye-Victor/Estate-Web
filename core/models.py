from django.db import models
from .choices import STATES, TYPE
import django
from django.conf import settings
from .validators import validate_image
from django.utils import timezone
from members.models import User 

# Create your models here.
User=settings.AUTH_USER_MODEL

#model handling the datatabase requirements cointaining all the property up for sale requirements.
class PropertyManagementSale(models.Model):
    user_id=models.IntegerField('Landlord', blank=False, default=1)
    company_uuid=models.CharField('Company', max_length=40, default='None', blank=True)
    agent_uuid= models.CharField('Agent', max_length=36, default='None', blank=True)
    property_description = models.TextField('Description')
    location = models.CharField('Location', max_length=255)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos')
    phone_number = models.CharField('Phone Number')
    owner = models.CharField('Listed By', max_length=120)
    price = models.DecimalField(max_digits=100,null=True, blank=True, decimal_places=2)
    bedrooms = models.IntegerField(default=1, blank=True, null=True)
    bathrooms = models.IntegerField(default=1, blank=True, null=True)
    parking_spaces=models.IntegerField(default=0)
    size= models.IntegerField('size', blank=True, default=0)
    available= models.BooleanField('Available', default=True)
    last_updated = models.DateTimeField(auto_now=True)#To pull out the last time the particular model was actually updated 
    compare=models.BooleanField('Compare', default=False)
    house_type= models.CharField(max_length=30, choices=TYPE, default='Bungalow')
    base_image= models.ImageField(null=True, blank=True, upload_to="images/buy", validators=[validate_image])
    listed_date=models.DateTimeField(default=timezone.now, blank=True)
    time_stamp=models.DateTimeField(null=True,blank=True, default=timezone.now)
    last_reset_date= models.DateTimeField(default=timezone.now)
    property_type=models.CharField('property Type', default='Sale')
    total_likes=models.IntegerField('Wishlisted time', default=0, blank=False, null=False)
    class NegotiateChoices(models.TextChoices):
        YES = 'Y', 'Yes'
        NO = 'N', 'No'

    negotiate = models.CharField(max_length=1, choices=NegotiateChoices.choices, default=NegotiateChoices.NO, blank=True, null=True)

    def __str__(self):
        return self.house_type


class PropertyManagementSaleAnalytics(models.Model):
    on_sale= models.ForeignKey(PropertyManagementSale, on_delete=models.CASCADE, related_name='prop_analytics')
    session_id= models.IntegerField('user_id', default=None)
    inquires_check=models.IntegerField('Inquiries', default=None)




#model handling the datatabase requirements cointaining all the property up for lease requirements
class PropertyManagementRent(models.Model):
    user_id=models.IntegerField('Landlord', blank=False, default=1)
    owner = models.CharField('Listed By', max_length=120)
    company_uuid=models.CharField('Company', max_length=36, default='None', blank=True)
    agent_uuid= models.CharField('Agent', max_length=36, default='None', blank=True)
    description= models.TextField('Description')
    location= models.CharField('Location', max_length=255)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos State')
    phone_number = models.CharField('Phone Number')
    price_range = models.DecimalField(max_digits=100, null=True, blank=True, decimal_places=2)
    available=models.BooleanField('Availble', default=True)
    bedrooms = models.IntegerField(default=1, blank=True, null=True)
    bathrooms = models.IntegerField(default=1, blank=True, null=True)
    size= models.IntegerField('size', blank=True, default=0)
    parking_spaces=models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    compare=models.BooleanField('Compare', default=False)
    house_type= models.CharField(max_length=30, choices=TYPE, default='Bungalow')
    base_image= models.ImageField(null=True, blank=True, upload_to="images/rent", validators=[validate_image])
    listed_date=models.DateTimeField(default=timezone.now, blank=True)
    time_stamp=models.DateTimeField(null=True,blank=True, default=timezone.now)
    last_reset_date= models.DateTimeField(default=timezone.now)
    property_type=models.CharField('property Type', default='Rent')
    total_likes=models.IntegerField('Wishlisted time', default=0, blank=False, null=False)
    def __str__(self):
        return self.house_type


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



class WishlistForRent(models.Model):
    property = models.ForeignKey('PropertyManagementRent', on_delete=models.CASCADE, related_name='wishlist_rent')
    whilist=models.BooleanField('Add to Whilist', default=False)
    users_id=models.IntegerField('User In question', default=1, blank=False, null=False)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.users_id} → {self.property.house_type}"


class WishlistForSale(models.Model):
    property = models.ForeignKey('PropertyManagementSale', on_delete=models.CASCADE, related_name='wishlist_sale')
    whilist=models.BooleanField('Add to Whilist', default=False)
    users_id=models.IntegerField('User In question', default=1, blank=False, null=False)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.users_id} → {self.property.house_type}"

class Feedback(models.Model):
    email=models.EmailField('Your Email')
    feedback= models.CharField(max_length=300, blank=False)
    date_sent= models.DateField(default=django.utils.timezone.now)



class WishlistStorageUnit(models.Model):
    user_id=models.IntegerField('Owner Of Wishlist', default=1, null=False, blank=False)
    property_id=models.IntegerField('Property In Question', default=1,null=False, blank=False)
    property_type=models.CharField('Property_type', default='Rent', null=False, blank=False)