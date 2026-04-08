from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    # Add a field to define the user's type
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('company', 'Company'),
        ('landlord', 'Landlord'),
    )
    role = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')   
    email=models.EmailField(unique=True)
    unique_user_id = models.CharField('uuid', max_length=36, default=uuid.uuid4, editable=False, unique=True)



# Set this in settings.py: AUTH_USER_MODEL = 'users.CustomUser'

