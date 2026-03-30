'''Models holding/Handling all our datatbases requirement used all through the website'''
from django.db import models
from django.utils import timezone
from core.choices import LEAD_STAGES, LEAD_STATUS, CONTACT_TYPE
import uuid



class LeadInfo(models.Model):
    name=models.CharField("Client's Name", max_length=50, blank=False)
    email=models.EmailField('Email to be contacted', max_length=100, blank= True)
    phone_no=models.CharField('Clients Phone Number', blank=False)
    property_intrested=models.IntegerField('Property in question', blank=True, default=None, null=True)
    inquiry_message= models.TextField('Client short mssg', blank=False)
    date_created=models.DateField('time created', default=timezone.now)
    date_updated=models.DateField('time updated', default=timezone.now)
    company_uuid=models.CharField('company uuid', max_length=36, blank=True, default=None, null=True)
    agent_id=models.CharField('Agents uuid', max_length=36, blank=True, default=None, null=True)
    landlord_id=models.CharField('Landlord uuid', max_length=36, blank=True, default=None, null=True)
    schedule_tour=models.DateField('Date for viewing', default=timezone.now, blank=True, null=True)
    contact_type=models.CharField('Media to get in touch', choices=CONTACT_TYPE, default='Whatsapp')
    property_type=models.CharField('Property Type', default=None)
    property_name=models.CharField('Property Name', default=None)
    status= models.CharField('Lead Status', choices=LEAD_STATUS, default='Not Contacted')
    stages= models.CharField('Lead Stages', choices=LEAD_STAGES, default='New')
    tags=models.CharField('tags', default='None')
    lead_id = models.CharField('lead uuid', max_length=36, default=uuid.uuid4, editable=False, unique=True)

