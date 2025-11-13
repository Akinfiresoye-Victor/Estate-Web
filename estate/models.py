'''Models holding/Handling all our datatbases requirement used all through the website'''

from django.db import models
from datetime import datetime
from .choices import STATES, TYPE, SOCIAL_LINKS, CONTACT_TYPE, LEAD_STATUS
import django
from django.conf import settings
from .validators import validate_image
from django.utils import timezone
from members.models import User 




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
    whilist=models.BooleanField('Add to Whilist', default=False)
    compare=models.BooleanField('Compare', default=False)
    house_type= models.CharField(max_length=30, choices=TYPE, default='Bungalow')
    base_image= models.ImageField(null=True, blank=True, upload_to="images/buy", validators=[validate_image])
    listed_date=models.DateTimeField(default=timezone.now, blank=True)
    time_stamp=models.DateTimeField(null=True,blank=True, default=timezone.now)
    last_reset_date= models.DateTimeField(default=timezone.now)
    property_type=models.CharField('property Type', default='Sale')
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
    owner = models.CharField('Listed By', max_length=120, default="Akinfiresoye")
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
    whilist=models.BooleanField('Add to Whilist', default=False)
    compare=models.BooleanField('Compare', default=False)
    house_type= models.CharField(max_length=30, choices=TYPE, default='Bungalow')
    base_image= models.ImageField(null=True, blank=True, upload_to="images/rent", validators=[validate_image])
    listed_date=models.DateTimeField(default=timezone.now, blank=True)
    time_stamp=models.DateTimeField(null=True,blank=True, default=timezone.now)
    last_reset_date= models.DateTimeField(default=timezone.now)
    property_type=models.CharField('property Type', default='Rent')
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
    property = models.ForeignKey('PropertyManagementRent', on_delete=models.CASCADE, related_name='wishlist')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('property', 'user')  # Prevent duplicates
    def __str__(self):
        return f"{self.user.username} → {self.property.house_type}"


class WishlistForSale(models.Model):
    property = models.ForeignKey('PropertyManagementSale', on_delete=models.CASCADE, related_name='wishlist')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('property', 'user')
    def __str__(self):
        return f"{self.user.username} → {self.property.house_type}"

class Feedback(models.Model):
    email=models.EmailField('Your Email')
    feedback= models.CharField(max_length=300, blank=False)
    date_sent= models.DateField(default=django.utils.timezone.now)
    





class UserInformation(models.Model):
    first_name = models.CharField('Professional First Name', max_length=30)
    last_name = models.CharField('Professional Last Name', max_length=30)
    phone_number = models.CharField('Phone Number', max_length=13) 
    email = models.EmailField('Email', max_length=100) 
    def __str__(self):
        return(self.first_name + ' ' +self.last_name)


class Agent_Information(models.Model):
    user_id= models.IntegerField(blank=False, default=1)
    personal_info = models.OneToOneField(UserInformation,on_delete=models.CASCADE, related_name='agent_profile')
    professional_title = models.CharField('Job Title', max_length=100) 
    professional_introduction = models.TextField('Profile Introduction', max_length=3000)
    call_to_action = models.CharField('CTA', max_length=50, blank=True)
    def __str__(self):
        return(self.personal_info.first_name)



class Experience(models.Model):
    # Foreign Key: Links multiple experiences back to ONE Agent_Information profile
    agent = models.ForeignKey(Agent_Information, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField('Company', max_length=200)
    title= models.CharField('Position', max_length=100)
    past_experence = models.CharField('Experience', max_length=100)
    start_date = models.DateField('Started')
    end_date = models.DateField('Ended', null=True, blank=True)    
    
    class Meta:
        unique_together = ('')
    def __str__(self):
        return(self.agent.personal_info.first_name)
    
class SocialLinks(models.Model):
    agent = models.ForeignKey(Agent_Information, on_delete=models.CASCADE, related_name='social')
    social_platform = models.CharField(max_length=20, choices=SOCIAL_LINKS, default='Instagram')
    link_to_social = models.URLField(max_length=200)
    class Meta:
        unique_together = ('social_platform', 'link_to_social')
    def __str__(self):
        return(self.agent.personal_info.first_name)
    
    

class LeadInfo(models.Model):
    name=models.CharField("Client's Name", max_length=50, blank=False)
    email=models.EmailField('Email to be contacted', max_length=100, blank= True)
    phone_no=models.CharField('Clients Phone Number', blank=False)
    property_intrested=models.IntegerField('Property in question', blank=False)
    inquiry_message= models.TextField('Client short mssg', blank=False)
    date_created=models.DateField('time created', default=timezone.now)
    company_uuid=models.CharField('company uuid', max_length=36, blank=True, default=None)
    agent_id=models.CharField('Agents uuid', max_length=36, blank=True, default=None)
    schedule_tour=models.DateField('Date for viewing', default=timezone.now)
    contact_type=models.CharField('Media to get in touch', choices=CONTACT_TYPE, default='Whatsapp')
    property_type=models.CharField('Property Type', default='Sale')
    property_name=models.CharField('Property Name', default='Bungalow')
    
    
    

class LeadStatus(models.Model):
    leads=models.ForeignKey(LeadInfo, on_delete=models.CASCADE, related_name='leads')
    status= models.CharField('Lead Status', choices=LEAD_STATUS, default='Not Contacted')
