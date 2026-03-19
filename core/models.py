from django.db import models
from .choices import *
from .validators import validate_image
from django.utils import timezone
from members.models import User 
import uuid
from django.conf import settings


#model handling the datatabase requirements cointaining all the property up for sale requirements.
class PropertyManagementSale(models.Model):
    users=models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user_id=models.IntegerField('Listee Users ID', blank=False, default=1)
    company_uuid=models.CharField('Company_uuid', max_length=40, default='None', blank=True)
    agent_uuid= models.CharField('Agent_uuid', max_length=36, default='None', blank=True)
    property_description = models.TextField('Description', max_length=200,blank=True)
    location = models.CharField('Location', max_length=100)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos')
    phone_number = models.CharField('Phone Number', max_length=12, blank=False)
    price = models.DecimalField(max_digits=100,null=False, blank=False, decimal_places=2, default=0)
    bedrooms = models.IntegerField(default=0, blank=True, null=True)
    bathrooms = models.IntegerField(default=0, blank=True, null=True)
    parking_spaces=models.IntegerField(default=0, blank=True, null=True)
    size= models.IntegerField('size', blank=True, default=300)
    available= models.BooleanField('Available', default=True)
    last_updated = models.DateTimeField(auto_now=True)
    property_category=models.CharField(choices=PROPERTY_CATEGORY, default='Residential')
    residential= models.CharField(max_length=30, choices=RESIDENTIAL_PROPERTIES, default='Apartment', blank=True)
    commercial= models.CharField(max_length=30, choices=COMMERCIAL_PROPERTIES, default='Office Space', blank=True)
    lands= models.CharField(max_length=30, choices=LAND, default='Farmland', blank=True)
    base_image= models.ImageField(null=True, blank=True, upload_to="images/buy", validators=[validate_image])
    listed_date=models.DateTimeField(default=timezone.now, blank=True)
    time_stamp=models.DateTimeField(null=True,blank=True, default=timezone.now)
    last_reset_date= models.DateTimeField(default=timezone.now)
    property_type=models.CharField('property Type', default='Sale')
    total_likes=models.IntegerField('Wishlisted time', default=0, blank=False, null=False)
    listing_score=models.IntegerField('Listing Score', default=0, blank=False, null=False)
    featured_listings=models.BooleanField('Featured Lising',default=False, blank=False, null=False )




#model handling the datatabase requirements cointaining all the property up for lease requirements
class PropertyManagementRent(models.Model):
    users=models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    user_id=models.IntegerField('Landlord', blank=False, default=1)
    company_uuid=models.CharField('Company', max_length=36, default='None', blank=True)
    agent_uuid= models.CharField('Agent', max_length=36, default='None', blank=True)
    description= models.TextField('Description',max_length=200, blank=True )
    location= models.CharField('Location', max_length=100, blank=False)
    state= models.CharField(max_length=20,choices=STATES, default='Lagos State')
    phone_number = models.CharField('Phone Number', max_length=12)
    price_range = models.DecimalField(max_digits=100, blank=False, decimal_places=2, default=0)
    available=models.BooleanField('Availble', default=True)
    bedrooms = models.IntegerField(default=0, blank=True, null=True)
    bathrooms = models.IntegerField(default=0, blank=True, null=True)
    size= models.IntegerField('size', blank=True, default=0)
    parking_spaces=models.IntegerField(default=0, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    property_category=models.CharField(choices=PROPERTY_CATEGORY,default='Residential')
    residential= models.CharField(max_length=30, choices=RESIDENTIAL_PROPERTIES, default='Apartment', blank=True)
    commercial= models.CharField(max_length=30, choices=COMMERCIAL_PROPERTIES, default='Office Space', blank=True)
    lands= models.CharField(max_length=30, choices=LAND, default='Farmland', blank=True)
    base_image= models.ImageField(null=True, blank=True, upload_to="images/rent", validators=[validate_image])
    listed_date=models.DateTimeField(default=timezone.now, blank=True)
    time_stamp=models.DateTimeField(null=True,blank=True, default=timezone.now)
    last_reset_date= models.DateTimeField(default=timezone.now)
    property_type=models.CharField('property Type', default='Rent')
    total_likes=models.IntegerField('Wishlisted time', default=0, blank=False, null=False)
    listing_score=models.IntegerField('Listing Score', default=0, blank=False, null=False)
    featured_listings=models.BooleanField('Featured Lising',default=False, blank=False, null=False )




'''Image Handling'''
class PropertySaleImage(models.Model):
    property= models.ForeignKey(PropertyManagementSale, on_delete=models.CASCADE, related_name='images')
    more_images= models.ImageField(null=True, blank=True, upload_to="images/buy", validators=[validate_image])
    caption=models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"{self.property} - image {self.pk}"

class PropertyRentImage(models.Model):
    property=models.ForeignKey(PropertyManagementRent, on_delete=models.CASCADE, related_name='images')
    more_images= models.ImageField(null=True, blank=True, upload_to="images/rent", validators=[validate_image])
    caption=models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"{self.property} - image {self.pk}"



class Feedbacks(models.Model):

    # ── Legacy fields — kept to protect any existing records ──────────
    # These were in the original model. Do NOT remove them.
    # New submissions won't use them but old ones still reference them.
    email      = models.EmailField('Your Email', blank=True, null=True)
    feedback   = models.CharField(max_length=300, blank=True, null=True)
    date_sent  = models.DateField(default=timezone.now)

    # ── New fields — added for the multi-channel feedback system ──────

    # The logged-in user who submitted. null=True means unauthenticated
    # users (or old records) won't cause errors. on_delete=SET_NULL means
    # if a user account is deleted, the feedback record stays — we don't
    # lose the data, just the link to who sent it.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks'
    )
    # Which type of user sent this. Max 10 chars covers all our role names.
    # blank=True so old records (which have no role) don't cause errors.
    ROLE_CHOICES = [
        ('agent',    'Agent'),
        ('company',  'Company Admin'),
        ('admin',    'Admin'),
        ('landlord', 'Landlord'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        blank=True,
        null=True
    )

    # The emoji reaction score: 1 (😡) to 5 (😍).
    # null=True protects old records that have no reaction score.
    reaction = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Emoji reaction score from 1 (worst) to 5 (best)'
    )

    # The category the user selected from the dropdown.
    CATEGORY_CHOICES = [
        ('bug',       'Bug Report'),
        ('feature',   'Feature Idea'),
        ('complaint', 'Complaint'),
        ('praise',    'Praise'),
    ]
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )

    # The open text field — "Tell us more..."
    # TextField (not CharField) because we don't limit how much they write.
    details = models.TextField(blank=True, null=True)

    # Optional screenshot — only uploaded on bug reports.
    # upload_to puts all screenshots in a dedicated folder inside MEDIA_ROOT.
    # null=True means this field is simply empty if no file was attached.
    screenshot = models.ImageField(
        upload_to='feedback_screenshots/',
        null=True,
        blank=True
    )

    # Auto-set to right now when the record is created. 
    # auto_now_add=True means Django sets this automatically —
    # you never have to pass it in your view.
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Most recent submissions appear first in queries and admin.
        ordering = ['-submitted_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback Submissions'

    def __str__(self):
        # What shows in the Django admin list view for each record.
        # Example: "agent • bug • 2026-03-14"
        role     = self.role     or 'unknown'
        category = self.category or 'general'
        date     = self.submitted_at.strftime('%Y-%m-%d') if self.submitted_at else str(self.date_sent)
        return f'{role} • {category} • {date}'


class WishlistStorageUnit(models.Model):
    user_id=models.IntegerField('Owner Of Wishlist', default=1, null=False, blank=False)
    property_id=models.IntegerField('Property In Question', default=1,null=False, blank=False)
    property_type=models.CharField('Property_type', default='Rent', null=False, blank=False)



class PropertyViews(models.Model):
    user_id=models.IntegerField('Users ID', default=1, blank=False, null=False)
    property_type=models.CharField('Property Type', default="Rent", blank=False, null=False)
    property_id=models.IntegerField('Property ID Viewed', default=1, blank=False, null=False)
    uuid=models.CharField('UUID',blank=False, null=False, default='da5dac64-3448-48a7-a209-4c84010d9ad2')


class Appointments(models.Model):
    company_uuid=models.CharField('Company UUID', default=None, blank=True, null=True)
    agent_uuid=models.CharField('Agents UUID', default=None, blank=True, null=True)
    lead_uuid=models.CharField('Lead UUID', default=None, blank=True, null=True)
    appointment=models.DateField('Appointment', default=timezone.now)
    note= models.CharField('Appointment Note', default='No Note Provided', blank=True, null=True)
    appointment_type=models.CharField('Appointment type',choices=APPOINTMENT_TYPE, default='Personal', blank=False, null=False)
    property_id=models.IntegerField('Property ID', default=None, blank=True, null=True)
    property_type=models.CharField('Property Type', default=None, blank=True, null=True)
    appointment_uuid=models.CharField('UUID', default=uuid.uuid4(), blank=False, null=False, unique=True)
    def __str__(self):
        return f'Appointment: {self.pk}- {self.note}'


# 1. New model for Property Types (Residential, Commercial, etc.)
class PropertyFocus(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "Property Focus Areas"

    def __str__(self):
        return self.name

# 2. New model for Partnership Goals (Boosts, Analytics, etc.)
class PartnershipGoal(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# 3. Your existing model with the new fields added at the bottom
class Partnership(models.Model):
    company_name = models.CharField('Company Name', max_length=100, null=False, blank=False)
    company_type = models.CharField('Company Type', choices=COMPANY_TYPE, default='other', blank=True)
    years_in_buisness = models.CharField('Years In Buisness', choices=YEARS_IN_BUISNESS, blank=True, default='Less than 1 year')
    team_size = models.CharField('Team Size', choices=TEAM_SIZE, blank=True, default='1-5 People')
    company_website = models.URLField('Company Website', max_length=200, null=True, blank=True)
    city = models.CharField('City', max_length=20, null=False, blank=False, default='Akure')
    state = models.CharField('State', choices=STATES, default='Lagos', blank=False )
    person_of_contact = models.CharField('Full Name', null=False, blank=False, max_length=70)
    person_position = models.CharField('Position', null=False, blank=False,  max_length=20)
    email = models.EmailField('Persons Email', null=False, blank=False, max_length=50)
    phone_number = models.CharField('Persons Phone Number', blank=False, null=False,max_length=12)
    average_listings = models.CharField('Mothly Listings', choices=AVERAGE_MONTHLY_LISTINGS, default='1-10 listings', null=True, blank=True)
    annual_revenue = models.CharField('Annual Revenue', choices=ESTIMATED_ANNUAL_REVENUE, default='Below ₦10 Million', null=False, blank=False)
    growth_goals = models.CharField('Growth Goals', null=True, blank=True, max_length=200)
    why_question = models.CharField('Why Partner with us', null=False, blank=False, max_length=200)
    property_types = models.ManyToManyField(PropertyFocus, blank=True)
    partnership_benefits = models.ManyToManyField(PartnershipGoal, blank=True)
    def __str__(self):
        return(f'{self.company_name}- {self.company_type}')
    