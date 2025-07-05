'''Models holding/Handling all our datatbases requirement used all through the website'''

from django.db import models
from datetime import datetime
from .choices import STATES


#model handling the datatabase requirements cointaining all the property up for sale requirements
class PropertyManagementSale(models.Model):
    user_id=models.IntegerField('Landlord', blank=False, default=1)
    summary=models.CharField('Short building tag', max_length=30, default=None)
    property_description = models.TextField('Description')
    location = models.CharField('Location', max_length=255)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos')
    phone_number = models.IntegerField('Phone Number')
    owner = models.CharField('Listed By', max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bedrooms = models.IntegerField(default=0, blank=True, null=True)
    bathrooms = models.IntegerField(default=0, blank=True, null=True)
    available= models.BooleanField('Available', default=True)
    last_updated = models.DateTimeField(auto_now=True)#To pull out the last time the particular model was actually updated 
    whilist=models.BooleanField('Add to Whilist', default=False)
    base_image= models.ImageField(null=True, blank=True, upload_to="images/buy")
    image1= models.ImageField(null=True, blank=True, upload_to="images/buy")
    image2= models.ImageField(null=True, blank=True, upload_to="images/buy")
    image3= models.ImageField(null=True, blank=True, upload_to="images/buy")
    image4= models.ImageField(null=True, blank=True, upload_to="images/buy")
    image5= models.ImageField(null=True, blank=True, upload_to="images/buy")
    image6= models.ImageField(null=True, blank=True, upload_to="images/buy")
    listed_date=models.DateTimeField(default=datetime.now, blank=True)
    
    class NegotiateChoices(models.TextChoices):
        YES = 'Y', 'Yes'
        NO = 'N', 'No'

    negotiate = models.CharField(max_length=1, choices=NegotiateChoices.choices, default=NegotiateChoices.NO, blank=True, null=True)

    def __str__(self):
        return self.summary




#model handling the datatabase requirements cointaining all the property up for lease requirements
class PropertyManagementRent(models.Model):
    user_id=models.IntegerField('Landlord', blank=False, default=1)
    owner = models.CharField('Listed By', max_length=120, default="Akinfiresoye")
    summary=models.CharField('Short building tag', max_length=30, default=None)
    description= models.TextField('Description')
    location= models.CharField('Location', max_length=255)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos State')
    phone_number = models.IntegerField('Phone Number')
    price_range = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available=models.BooleanField('Availble', default=True)
    bedrooms = models.IntegerField(default=1, blank=True, null=True)
    bathrooms = models.IntegerField(default=1, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    whilist=models.BooleanField('Add to Whilist', default=False)
    base_image= models.ImageField(null=True, blank=True, upload_to="images/rent")
    image1= models.ImageField(null=True, blank=True, upload_to="images/rent")
    image2= models.ImageField(null=True, blank=True, upload_to="images/rent")
    image3= models.ImageField(null=True, blank=True, upload_to="images/rent")
    image4= models.ImageField(null=True, blank=True, upload_to="images/rent")
    image5= models.ImageField(null=True, blank=True, upload_to="images/rent")
    image6= models.ImageField(null=True, blank=True, upload_to="images/rent")
    listed_date=models.DateTimeField(default=datetime.now, blank=True)
    def __str__(self):
        return self.summary




