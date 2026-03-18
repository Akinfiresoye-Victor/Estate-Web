from django.db import models
from core.choices import STATES, SOCIAL_LINKS,AGENT_STATUS
from core.validators import validate_image, validate_file
import uuid
from members.models import User
from django.utils import timezone
from datetime import timedelta


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
    date_joined=models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.company_name




class Employees(models.Model):
    company=models.ForeignKey(CompanyInformation, on_delete=models.CASCADE, related_name='employee')
    agent_name=models.CharField('Full Name', max_length=50, blank=False, null=False)
    company_department=models.CharField('Agent Department', max_length=20, blank=True, null=True)
    company_role=models.CharField('Agent Role', max_length=50, blank=False, null=False)
    agent_email=models.EmailField('Agent Email', blank=True, null=True,max_length=75)
    agent_phone_no=models.CharField('Phone No', blank=False, max_length=12)
    agent_uuid=models.CharField('Agent UUID', unique=True, max_length=36, blank=False)
    date_joined=models.DateField(auto_now_add=True)
    agent_status=models.CharField(choices=AGENT_STATUS, blank=False, default='Active')
    agent_headshot=models.ImageField('Agent Picture', blank=True)
    def __str__(self):
        return(f'{self.company}-- {self.agent_name}--{self.company_department}')




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
    average_profile_views=models.IntegerField('last month profile views',default=1)
    average_lease_views=models.IntegerField('last month lease views',default=1)
    average_sale_views=models.IntegerField('last month sale views',default=1)
    competition= models.IntegerField('competition', default=0)
    def __str__(self):
        return(self.company.company_name)
    

class SessionId(models.Model):
    company=models.ForeignKey(CompanyInformation, on_delete=models.CASCADE, related_name='session_id')
    session_id=models.IntegerField('user session id',default=None)
    inquires_check=models.IntegerField('inq', default= 0)




class CompanyRating(models.Model):
    company_uuid = models.CharField('Companies UUID', max_length=255, blank=False, null=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='company_reviews')
    rating = models.FloatField('Rating', blank=False, default=0.0)
    comment = models.TextField('Review Comment', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('company_uuid', 'user')  # Prevents duplicate reviews from same user
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rating} stars"



class JobPost(models.Model):
    # Existing fields (unchanged)
    user_id = models.IntegerField('Company ID', default=1, blank=False, null=False)
    company_uuid = models.CharField('Company UUID', default=uuid.uuid4, blank=False, null=False, max_length=36)  # Fixed: removed () from uuid.uuid4
    job_title = models.CharField('Job Title', default='', blank=False, null=True, max_length=100)
    job_type = models.CharField('Full/Part time', default='', blank=False, null=False, max_length=20)
    job_location = models.CharField('Location', default='', blank=False, null=False, max_length=100)  # Increased from 11 to 100
    short_description = models.CharField('Short Desc', default='', max_length=250, blank=False, null=False)  # Changed default=None to ''
    full_description = models.TextField('Full Desc', blank=True, null=True)  # Changed from CharField to TextField
    min_pay = models.DecimalField('Min Salary', max_digits=10, decimal_places=2, blank=True, null=True)  # Changed from FloatField to DecimalField
    max_pay = models.DecimalField('Max Salary', max_digits=10, decimal_places=2, blank=True, null=True)  # Changed from FloatField to DecimalField
    applicants = models.IntegerField('Applicants Number', default=0, blank=True, null=False)
    shortlisted = models.IntegerField('Shortlisted Number', default=0, blank=True, null=False)
    pending_applicants = models.IntegerField('Pending', default=0, blank=True, null=True)
    date_posted = models.DateField('Date Posted', default=timezone.now)
    date_updated = models.DateField('Date Updated', default=timezone.now)
    
    # New essential fields
    experience_required = models.CharField('Experience Required', max_length=50, blank=True, null=True, 
                                          help_text='e.g., 2-5 years, Entry Level, Senior')
    education_required = models.CharField('Education Required', max_length=100, blank=True, null=True,
                                         help_text='e.g., Bachelor\'s Degree, High School, etc.')
    skills_required = models.TextField('Skills Required', blank=True, null=True,
                                      help_text='Comma-separated list of required skills')
    responsibilities = models.TextField('Key Responsibilities', blank=True, null=True,
                                       help_text='List of main job responsibilities')
    benefits = models.TextField('Benefits & Perks', blank=True, null=True,
                               help_text='e.g., Health insurance, Remote work, etc.')
    
    # Additional useful fields
    application_deadline = models.DateField('Application Deadline', blank=True, null=True)
    is_active = models.BooleanField('Active', default=True, help_text='Is this job posting currently active?')
    is_featured = models.BooleanField('Featured', default=False, help_text='Feature this job on homepage')
    salary_currency = models.CharField('Currency', max_length=10, default='NGN', blank=True)
    salary_period = models.CharField('Salary Period', max_length=20, default='Monthly', 
                                    choices=[
                                        ('Hourly', 'Per Hour'),
                                        ('Daily', 'Per Day'),
                                        ('Weekly', 'Per Week'),
                                        ('Monthly', 'Per Month'),
                                        ('Yearly', 'Per Year'),
                                    ])
    positions_available = models.IntegerField('Number of Positions', default=1, 
                                            help_text='How many people are you hiring?')
    
    class Meta:
        ordering = ['-date_posted']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
    
    def __str__(self):
        return f"{self.job_title} - {self.job_type}-{self.pk}"
    
    def save(self, *args, **kwargs):
        # Update date_updated on every save
        self.date_updated = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if job posting has expired"""
        if self.application_deadline:
            return timezone.now().date() > self.application_deadline
        return False
    
    @property
    def days_remaining(self):
        """Calculate days remaining until deadline"""
        if self.application_deadline:
            delta = self.application_deadline - timezone.now().date()
            return delta.days if delta.days >= 0 else 0
        return None

class Applications(models.Model):
    job=models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='job_applications')
    applicants_uuid=models.CharField('applicant_uuid', null=False, blank=False, default=uuid.uuid4)
    applicants_resume=models.FileField('Applicants Resume', null=True, blank=True)
    date_posted=models.DateField('Date Posted', default=timezone.now)
    date_updated=models.DateField('Date Updated', default=timezone.now)

class CompanyActivityLog(models.Model):
    company = models.ForeignKey(CompanyInformation, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField('Activity Description', max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    



class InviteLink(models.Model):
    company=models.ForeignKey(CompanyInformation, on_delete=models.CASCADE, related_name='invite_link')
    invite_token=models.CharField('Link UUID', max_length=36, default=uuid.uuid4, editable=False, unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    expires_at=models.DateTimeField('Date To expire', default=timezone.now() + timedelta(hours=24))#default of 24 hours
    max_uses=models.IntegerField('Usage Possibility', default=200, null=True, blank=True)
    use_count=models.IntegerField('Use Count', default=0, null=False, blank=False)
    is_active= models.BooleanField('Is Link Active?',default=True )



class CompanyAnnouncements(models.Model):
    company=models.ForeignKey(CompanyInformation, on_delete=models.CASCADE, related_name='company_announcements')
    announcements=models.CharField('Announcemt', max_length=100, default=None, null=False, blank=False)
    time_created=models.DateTimeField(auto_now_add=True)