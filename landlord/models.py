from django.db import models
from core.choices import STATES, LANDLORD_TIER
from core.validators import validate_image, validate_file
import uuid
from members.models import User
from django.utils import timezone
from django.conf import settings

def landlord_picture_path(instance, filename):
    return f"Landlord/{instance.first_name}/profile/{filename}"

class LandlordInformation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField('First Name', max_length=50, blank=False, default='Unspecified')
    last_name = models.CharField('Last Name', max_length=50, blank=False, default='Unspecified')
    landlord_uuid = models.CharField('Landlord uuid', unique=True, max_length=36, blank=False, default=uuid.uuid4)
    phone_number = models.CharField('Phone.No', blank=False, max_length=12)
    email = models.EmailField('Email', blank=True, max_length=75)
    location = models.CharField('Base City', blank=False, choices=STATES, default='Lagos')
    landlord_tier= models.CharField(choices=LANDLORD_TIER, default='aggressive')
    profile_picture = models.ImageField('Profile Picture', blank=True, upload_to=landlord_picture_path, validators=[validate_image], null=True)
    government_id = models.FileField('Government ID', blank=True, null=True, upload_to='landlord/ID', validators=[validate_file])
    verified = models.BooleanField('Verified landlord', default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

