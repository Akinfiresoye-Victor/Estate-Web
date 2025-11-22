'''Models holding/Handling all our datatbases requirement used all through the website'''

from django.db import models
from django.conf import settings
from django.utils import timezone
from core.choices import LEAD_STAGES, LEAD_STATUS, CONTACT_TYPE









class UserInformation(models.Model):
    first_name = models.CharField('Professional First Name', max_length=30)
    last_name = models.CharField('Professional Last Name', max_length=30)
    phone_number = models.CharField('Phone Number', max_length=13) 
    email = models.EmailField('Email', max_length=100) 
    def __str__(self):
        return(self.first_name + ' ' +self.last_name)




class LeadInfo(models.Model):
    name=models.CharField("Client's Name", max_length=50, blank=False)
    email=models.EmailField('Email to be contacted', max_length=100, blank= True)
    phone_no=models.CharField('Clients Phone Number', blank=False)
    property_intrested=models.IntegerField('Property in question', blank=False)
    inquiry_message= models.TextField('Client short mssg', blank=False)
    date_created=models.DateField('time created', default=timezone.now)
    date_updated=models.DateField('time updated', default=timezone.now)
    company_uuid=models.CharField('company uuid', max_length=36, blank=True, default=None)
    agent_id=models.CharField('Agents uuid', max_length=36, blank=True, default=None)
    schedule_tour=models.DateField('Date for viewing', default=timezone.now, blank=True, null=True)
    contact_type=models.CharField('Media to get in touch', choices=CONTACT_TYPE, default='Whatsapp')
    property_type=models.CharField('Property Type', default='Sale')
    property_name=models.CharField('Property Name', default='Bungalow')
    status= models.CharField('Lead Status', choices=LEAD_STATUS, default='Not Contacted')
    stages= models.CharField('Lead Stages', choices=LEAD_STAGES, default='New')
    tags=models.CharField('tags', default='None')