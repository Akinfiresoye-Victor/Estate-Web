from django.db import models
from core.choices import STATES, AGENT_SOCIAL_LINKS, YEARS_OF_EXPERINCE
from core.validators import validate_image, validate_file
import uuid



def agent_picture_path(instance, filename):
    return f"Agent/{instance.profile_name}/profile/{filename}"


def company_file_path(instance, filename):
    return f"Agent/{instance.profile_name}/ID/{filename}"



# Create your models here.
class AgentInformation(models.Model):
    user_id = models.IntegerField(blank=False)
    profile_name = models.CharField('Full Name', max_length=100, blank=False)
    agent_uuid = models.CharField('Agent uuid', unique=True, max_length=36, blank=False, default=uuid.uuid4)
    company_uuid = models.CharField('Company uuid', blank=True, null=True, max_length=36)
    universal_agent = models.BooleanField('Universal agent', default=False)
    phone_number = models.CharField('Phone.No', blank=False, max_length=12)
    email = models.EmailField('Email', blank=True, max_length=100)
    location = models.CharField('Base City', blank=False, choices=STATES)
    language = models.CharField('language Spoken', blank=False, max_length=100)
    bio = models.TextField('Work Summary')
    work_type = models.CharField('Nature of work', blank=False, max_length=100)
    profile_picture = models.ImageField('Profile Picture', blank=True, upload_to=agent_picture_path, validators=[validate_image], null=True)
    government_id = models.FileField('Government ID', blank=True, null=True, upload_to='agent/ID', validators=[validate_file])
    certificate = models.FileField('Professional Certificate', blank=True, null=True)
    verified = models.BooleanField('Verified agent', default=False)
    def __str__(self):
        return self.profile_name

class Experience(models.Model):
    # Foreign Key: Links multiple experiences back to ONE AgentInformation profile
    agent = models.ForeignKey(AgentInformation, on_delete=models.CASCADE, related_name='experiences')
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
    agent = models.ForeignKey(AgentInformation, on_delete=models.CASCADE, related_name='social')
    social_platform = models.CharField(max_length=20, choices=AGENT_SOCIAL_LINKS, default='Instagram', blank=True)
    link_to_social = models.URLField(max_length=200, blank=True)
    def __str__(self):
        return(self.agent.personal_info.first_name)


class UniversalAgent(models.Model):
    agent=models.ForeignKey(AgentInformation, on_delete=models.CASCADE, related_name='universal')
    years_experience=models.CharField('Years Of Experience',default='0-1', choices=YEARS_OF_EXPERINCE)
    agency=models.BooleanField('Affiliated With Agency?', default=False)
    agency_name=models.CharField('Agency Name', default='Not With Agency', max_length=50)