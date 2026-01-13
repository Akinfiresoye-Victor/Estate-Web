from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import *





# forms.py
class AgentInformationForm(ModelForm):
    class Meta:
        model = AgentInformation
        fields = (
            'profile_name','language', 'work_type', 'bio','profile_picture', 'phone_number',
            'email', 'location','certificate','government_id', 'universal_agent'
        )
        labels = {
            'profile_name': 'Professional Name',
            'language': 'Language Spoken',
            'work_type': 'Nature Of Work',
            'bio': 'Professional Summary',
            'profile_picture': '',
            'phone_number': 'Phone No.',
            'email': 'Email',
            'location': 'Base City',
            'certificate': 'Certificate To prove yourself',
            'government_id': 'ID Card, Passport, Drivers Liscence,NIN Slip',
            'universal_agent': 'Are you walking alone?'
        }
        widgets = {
            'profile_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g English, French'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Professional Summary'}),
            'work_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Realtor, Consultant'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clear initial values for new forms
        if not self.instance.pk:
            self.fields['profile_name'].initial = ''
            self.fields['phone_number'].initial = ''
            self.fields['email'].initial = ''
            self.fields['language'].initial = ''
            self.fields['bio'].initial = ''
            self.fields['work_type'].initial = ''
            self.fields['location'].initial = ''
            

class UniversalAgentForm(ModelForm):
    class Meta:
        model=UniversalAgent
        fields=(
            'years_experience', 'agency', 'agency_name'
        )
        labels={
            'years_experience':'', 
            'agency': '', 
            'agency_name': ''
        }
        widgets={
            'agency_name': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Agency Name'})
        }

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = ['company','title', 'start_date', 'end_date']
        label={
            'company': '',
            'title': '',
        }
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Estate Web Inc.'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Real Estate Agent'}),
            'start_date': forms.DateInput(attrs={'type': 'date','class': 'form-control','placeholder': 'Select start date'}),
            'end_date': forms.DateInput(attrs={'type': 'date','class': 'form-control','placeholder': 'Select end date'}),
        }



'''formset'''
ExperienceFormSet = inlineformset_factory(
    AgentInformation, 
    Experience,        
    form= ExperienceForm,
    can_delete=True,
    
)

SocialLinksFormSet= inlineformset_factory(
    AgentInformation,
    SocialLinks,
    fields=('social_platform', 'link_to_social'),
    can_delete=True
)