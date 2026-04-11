from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import *





from django import forms
from django.forms import inlineformset_factory
from .models import AgentInformation, Experience, SocialLinks

class AgentInformationForm(forms.ModelForm):
    """Main agent information form"""
    
    class Meta:
        model = AgentInformation
        fields = [
            'phone_number', 'location', 
            'language', 'work_type', 'bio', 'profile_picture', 
            'government_id', 'certificate'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
            'language': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. English, French'
            }),
            'work_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Realtor, Consultant'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*'
            }),
            'government_id': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'certificate': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }


class UpdateAgentInformationForm(forms.ModelForm):
    """Main agent information form"""
    
    class Meta:
        model = AgentInformation
        fields = [
            'first_name','last_name','phone_number', 'email', 'location', 
            'language', 'work_type', 'bio', 'profile_picture', 
            'government_id', 'certificate'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ahmed'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ibrahim'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'email': forms.EmailInput(attrs={
                'readonly':'readonly',
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
            'language': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. English, French'
            }),
            'work_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Realtor, Consultant'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...',
                'rows': 4
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*'
            }),
            'government_id': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
            'certificate': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
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


# FIXME agents cant change their Ful Name
'''formset'''
ExperienceFormSet = inlineformset_factory(
    AgentInformation,
    Experience,
    fields=['company', 'title', 'start_date', 'end_date'],
    extra=1,  # Show 1 empty form by default
    can_delete=True,  # Allow deletion of forms
    widgets={
        'company': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name'
        }),
        'title': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title'
        }),
        'start_date': forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        'end_date': forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
    }
)

# Social Links Formset Configuration
SocialLinksFormSet = inlineformset_factory(
    AgentInformation,
    SocialLinks,
    fields=['social_platform', 'link_to_social'],
    extra=1,  # Show 1 empty form by default
    can_delete=True,  # Allow deletion of forms
    widgets={
        'social_platform': forms.Select(attrs={
            'class': 'form-control'
        }),
        'link_to_social': forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/profile'
        }),
    }
)

