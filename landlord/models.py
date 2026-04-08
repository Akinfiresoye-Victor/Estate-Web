from django.db import models
from core.choices import STATES
from core.validators import validate_image, validate_file
import uuid
from members.models import User
from django.utils import timezone

def landlord_picture_path(instance, filename):
    return f"Landlord/{instance.first_name}/profile/{filename}"

class LandlordInformation(models.Model):
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    user_id = models.IntegerField(blank=False)
    first_name = models.CharField('First Name', max_length=50, blank=False, default='Unspecified')
    last_name = models.CharField('Last Name', max_length=50, blank=False, default='Unspecified')
    landlord_uuid = models.CharField('Landlord uuid', unique=True, max_length=36, blank=False, default=uuid.uuid4)
    phone_number = models.CharField('Phone.No', blank=False, max_length=12)
    email = models.EmailField('Email', blank=True, max_length=75)
    location = models.CharField('Base City', blank=False, choices=STATES, default='Lagos')
    profile_picture = models.ImageField('Profile Picture', blank=True, upload_to=landlord_picture_path, validators=[validate_image], null=True)
    government_id = models.FileField('Government ID', blank=True, null=True, upload_to='landlord/ID', validators=[validate_file])
    inventory_slots = models.IntegerField('Inventory Slots', default=3)
    listing_slots = models.IntegerField('Listing Slots', default=2)
    verified = models.BooleanField('Verified landlord', default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

