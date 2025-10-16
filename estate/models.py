'''Models holding/Handling all our datatbases requirement used all through the website'''

from django.db import models
from datetime import datetime
from .choices import STATES
import django
from django.contrib.auth.models import User


#model handling the datatabase requirements cointaining all the property up for sale requirements.
class PropertyManagementSale(models.Model):
    user_id=models.IntegerField('Landlord', blank=False, default=1)
    summary=models.CharField('Short building tag', max_length=30, default=None)
    property_description = models.TextField('Description')
    location = models.CharField('Location', max_length=255)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos')
    phone_number = models.CharField('Phone Number')
    owner = models.CharField('Listed By', max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bedrooms = models.IntegerField(default=0, blank=True, null=True)
    bathrooms = models.IntegerField(default=0, blank=True, null=True)
    available= models.BooleanField('Available', default=True)
    last_updated = models.DateTimeField(auto_now=True)#To pull out the last time the particular model was actually updated 
    whilist=models.BooleanField('Add to Whilist', default=False)
    compare=models.BooleanField('Compare', default=False)
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
    phone_number = models.CharField('Phone Number')
    price_range = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available=models.BooleanField('Availble', default=True)
    bedrooms = models.IntegerField(default=1, blank=True, null=True)
    bathrooms = models.IntegerField(default=1, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    whilist=models.BooleanField('Add to Whilist', default=False)
    compare=models.BooleanField('Compare', default=False)
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





class WishlistForRent(models.Model):
    property = models.ForeignKey('PropertyManagementRent', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('property', 'user')  # Prevent duplicates
    def __str__(self):
        return f"{self.user.username} → {self.property.summary}"


class WishlistForSale(models.Model):
    property = models.ForeignKey('PropertyManagementSale', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('property', 'user')
    def __str__(self):
        return f"{self.user.username} → {self.property.summary}"

class Feedback(models.Model):
    email=models.EmailField('Your Email')
    feedback= models.CharField(max_length=300, blank=False)
    date_sent= models.DateField(default=django.utils.timezone.now)
    

class Room(models.Model):
    room_name=models.CharField(max_length=20)

    def __str__(self):
        return str(self.room_name)


class Messages(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return str(self.room)