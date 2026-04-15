from django.db import models
from core.choices import STATES, AGENT_SOCIAL_LINKS,AGENT_TIER
from core.validators import validate_image, validate_file
import uuid
from members.models import User
from django.utils import timezone
from django.conf import settings



def agent_picture_path(instance, filename):
    return f"Agent/{instance.first_name}/profile/{filename}"





# Create your models here.
class AgentInformation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField('First Name', max_length=50, blank=False, default='Unspecified')
    last_name = models.CharField('Last Name', max_length=50, blank=False, default='j')
    agent_uuid = models.CharField('Agent uuid', unique=True, max_length=36, blank=False, default=uuid.uuid4)
    company_uuid = models.CharField('Company uuid', blank=True, null=True, max_length=36, db_index=True)
    phone_number = models.CharField('Phone.No', blank=False, max_length=12)
    email = models.EmailField('Email', blank=True, max_length=75)
    location = models.CharField('Base City', blank=False, choices=STATES)
    language = models.CharField('language Spoken', blank=False, max_length=100)
    bio = models.TextField('About You?', max_length=1024)
    work_type = models.CharField('Nature of work', blank=False, max_length=100)
    profile_picture = models.ImageField('Profile Picture', blank=True, upload_to=agent_picture_path, validators=[validate_image], null=True)
    government_id = models.FileField('Government ID', blank=True, null=True, upload_to='agent/ID', validators=[validate_file])
    certificate = models.FileField('Professional Certificate', blank=True, null=True, upload_to='agent/certificates', validators=[validate_file])
    verified = models.BooleanField('Verified agent', default=False)
    date_joined=models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.first_name}-{self.last_name}'


class Experience(models.Model):
    # Foreign Key: Links multiple experiences back to ONE AgentInformation profile
    agent = models.ForeignKey(AgentInformation, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField('Company', max_length=70)
    title= models.CharField('Position', max_length=40)
    past_experence = models.CharField('Experience', max_length=100)
    start_date = models.DateField('Started')
    end_date = models.DateField('Ended', null=True, blank=True)    
    

    def __str__(self):
        return(f'{self.agent.first_name} {self.agent.last_name}')
    
class SocialLinks(models.Model):
    agent = models.ForeignKey(AgentInformation, on_delete=models.CASCADE, related_name='social')
    social_platform = models.CharField(max_length=20, choices=AGENT_SOCIAL_LINKS, blank=False)
    link_to_social = models.URLField(max_length=200, blank=False)
    def __str__(self):
        return(f'{self.agent.first_name} {self.agent.last_name}')

class AgentAnalytics(models.Model):
    agent = models.OneToOneField(AgentInformation, on_delete=models.CASCADE, related_name='analytics')
    profile_views = models.IntegerField('Profile Views', default=0, null=False, blank=True)
    property_views_l = models.IntegerField('Lease Property Views', default=0, null=False, blank=True)
    property_views_s = models.IntegerField('Sale Property Views', default=0, null=False, blank=True)
    average_profile_views = models.IntegerField('Average Profile Views', default=0, null=False, blank=True)
    average_lease_views = models.IntegerField('Average Lease Views', default=0, null=False, blank=True)
    average_sale_views = models.IntegerField('Average Sale Views', default=0, null=False, blank=True)
    last_reset_date = models.DateTimeField('Last Reset Date', default=timezone.now)
    competition = models.FloatField('Engagement Score', default=0.0, blank=True, null=True)
    ratings = models.FloatField('Agent Rating', default=0.0, blank=True, null=True)
    reviews = models.IntegerField('Number Of Reviews', default=0, blank=True, null=True)
    monthly_leads    = models.IntegerField(default=0)
    monthly_reviews  = models.IntegerField(default=0)
    average_leads    = models.IntegerField(default=0)
    average_reviews  = models.IntegerField(default=0)
    
    def __str__(self):
        return(f'{self.agent.first_name} {self.agent.last_name} - Analytics')

class SessionId(models.Model):
    agent=models.ForeignKey(AgentInformation, on_delete= models.CASCADE, related_name='session_id')
    session_id= models.IntegerField('Users Session ID', default=None)
    inquires_check=models.IntegerField('inq', default=0)


class AgentRating(models.Model):
    agent_uuid=models.CharField('Agent UUID', max_length=255, blank=False, null=False)
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='agent_reviews')
    rating= models.FloatField('Rating', blank=False, default=0.0)
    comment=models.TextField('Review Comment', blank=True, null=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together= ('agent_uuid', 'user')
        ordering= ['-created_at']
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rating} stars" 

