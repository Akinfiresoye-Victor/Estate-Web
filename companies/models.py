from django.db import models
from core.choices import STATES, SOCIAL_LINKS
from core.validators import validate_image, validate_file
import uuid
from members.models import User
from django.utils import timezone

def company_logo_path(instance, filename):
    return f"company/logo/{instance.company_name}/{filename}"



def company_file_path(instance, filename):
    return f"company/certificate/{instance.company_name}/{filename}"



class CompanyInformation(models.Model):
    users=models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user_id= models.IntegerField(blank=False, default=1)
    unique_company_id = models.CharField('uuid', max_length=36, default=uuid.uuid4, editable=False, unique=True)
    company_name= models.CharField('Company Name', blank=False, max_length=100, unique=True)
    legal_certificate= models.FileField('Certificate of Incoperation',blank=True, null=True, upload_to=company_file_path, validators=[validate_file])
    year_established= models.IntegerField('Year Established',blank=False,)
    phone_number=models.CharField('Phone Number',blank=False, max_length=11)
    email=models.EmailField('Company Email', blank=False, max_length=40, unique=True)
    address=models.CharField('Company Adress', blank=False, max_length=100)
    service_areas= models.CharField(max_length=20,choices=STATES, default='Lagos')
    company_bio=models.TextField('Brief Company Overview', blank=False, max_length=500, unique=True)
    company_logo=models.ImageField('Company Logo', blank=True, upload_to=company_logo_path, validators=[validate_image], null=True)
    principal_broker= models.CharField('Registered Owner of Company', max_length=100)
    time_created=models.DateTimeField(default=timezone.now, blank=False)
    verified=models.BooleanField('Verified Company',default=False)
    def __str__(self):
        return self.company_name



class CompanySocialLinks(models.Model):
    company = models.ForeignKey(CompanyInformation, on_delete=models.CASCADE, related_name='social')
    social_platform = models.CharField(max_length=20, choices=SOCIAL_LINKS, default='Company Website')
    link_to_social = models.URLField(max_length=200)
    class Meta:
        unique_together = ('social_platform', 'link_to_social')
    def __str__(self):
        return(self.company.company_name)

class CompanyAnalytics(models.Model):
    company=models.ForeignKey(CompanyInformation, on_delete=models.CASCADE, related_name='analytics')
    profile_views=models.IntegerField('Total Profile Views', default=0)
    property_views_s=models.IntegerField('Listed Property views Sale', default=0)
    property_views_l=models.IntegerField('Listed Property views Lease', default=0)
    last_reset_date = models.DateTimeField('last reset date',default=timezone.now)
    last_month_profile_views=models.IntegerField('last month profile views',default=1)
    last_month_lease_views=models.IntegerField('last month lease views',default=1)
    last_month_sale_views=models.IntegerField('last month sale views',default=1)
    
    competition= models.IntegerField('competition', default=0)
    def __str__(self):
        return(self.company.company_name)
    

class SessionId(models.Model):
    company=models.ForeignKey(CompanyInformation, on_delete=models.CASCADE, related_name='session_id')
    session_id=models.IntegerField('user session id',default=None)
    inquires_check=models.IntegerField('inq', default= 0)




class CompanyRating(models.Model):
    company_uuid = models.CharField('Companies UUID', max_length=255, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_reviews')
    rating = models.FloatField('Rating', blank=False, default=0.0)
    comment = models.TextField('Review Comment', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('company_uuid', 'user')  # Prevents duplicate reviews from same user
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rating} stars"
