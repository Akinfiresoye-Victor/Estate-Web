from django import forms
from django.forms import ModelForm
from .models import CompanyInformation, CompanySocialLinks,JobPost, InviteLink
from core.choices import STATES, EXPIRY_CHOICES
from django.forms import formset_factory, inlineformset_factory
from django.core.exceptions import ValidationError


class CompanyForm(ModelForm):
    class Meta:
        model=CompanyInformation
        fields=(
        'company_name', 'company_bio', 'year_established', 'company_logo', 'phone_number', 'email', 'address', 
        'service_areas', 'principal_broker','legal_certificate'
        )
        labels={
            'company_name': 'Company/Organization Name*',
            'combany_bio': 'Company/Organization Bio*',
            'year_established': 'Year Established*',
            'company_logo': 'Company Logo',
            'phone_number': 'Registered Company Number*',
            'email': 'Registered Email*',
            'address': 'Company Address*' ,
            'service_areas': 'State Functioning*',
            'principal_broker': 'Registered Owner of Business*', 
            'legal_certificate': 'Oficial Legal Certificate(optional.. For Verification Purpose)'
        }
        widgets={
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Companies Full Description'}),
            'year_established': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g 2025,2013'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'principal_broker': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

SocialLinksFormset= inlineformset_factory(
    CompanyInformation,
    CompanySocialLinks,
    fields=('social_platform', 'link_to_social'),
    extra=1,
    can_delete=True
)



from django import forms
from .models import JobPost

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = (
            # Existing fields (unchanged)
            'job_title', 'job_type', 'job_location', 
            'short_description', 'full_description', 
            'min_pay', 'max_pay',
            # New fields
            'salary_currency', 'salary_period', 'positions_available',
            'experience_required', 'education_required', 
            'skills_required', 'responsibilities', 'benefits',
            'application_deadline', 'is_active', 'is_featured'
        )
        labels = {
            # Existing labels (unchanged)
            'job_title': '',
            'job_type': '',
            'job_location': '',
            'short_description': '',
            'full_description': '',
            'min_pay': '',
            'max_pay': '',
            # New labels
            'salary_currency': '',
            'salary_period': '',
            'positions_available': '',
            'experience_required': '',
            'education_required': '',
            'skills_required': '',
            'responsibilities': '',
            'benefits': '',
            'application_deadline': '',
            'is_active': 'Keep this job posting active',
            'is_featured': 'Feature this job on homepage'
        }
        widgets = {
            # Existing widgets (unchanged)
            'job_title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g Real Estate Agent, Property Manager',
                'required': True
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }, choices=[
                ('', 'Select Job Type'),
                ('Full-Time', 'Full-Time'),
                ('Part-Time', 'Part-Time'),
                ('Contract', 'Contract'),
                ('Internship', 'Internship'),
                ('Freelance', 'Freelance'),
            ]),
            'job_location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g Lagos, Remote, Hybrid',
                'required': True
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Brief overview of the position (max 250 characters)',
                'maxlength': '250',
                'required': True
            }),
            'full_description': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Detailed job description, responsibilities, requirements, and benefits',
                'rows': 8
            }),
            'min_pay': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'max_pay': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            
            # New field widgets
            'salary_currency': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('NGN', '₦ Naira'),
                ('USD', '$ Dollar'),
                ('GBP', '£ Pound'),
                ('EUR', '€ Euro'),
            ]),
            'salary_period': forms.Select(attrs={
                'class': 'form-control'
            }),
            'positions_available': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1',
                'min': '1',
                'value': '1'
            }),
            'experience_required': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2-5 years, Entry Level, Senior Level'
            }),
            'education_required': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bachelor\'s Degree in relevant field'
            }),
            'skills_required': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List required skills (one per line or comma-separated)',
                'rows': 4
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List key job responsibilities (one per line)',
                'rows': 6
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Health insurance, Remote work, Professional development, etc.',
                'rows': 4
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': '',  # Will be set dynamically in __init__
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set minimum date for application_deadline to today
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        self.fields['application_deadline'].widget.attrs['min'] = today
        
        # Make certain fields optional
        self.fields['experience_required'].required = False
        self.fields['education_required'].required = False
        self.fields['skills_required'].required = False
        self.fields['responsibilities'].required = False
        self.fields['benefits'].required = False
        self.fields['application_deadline'].required = False
        self.fields['min_pay'].required = False
        self.fields['max_pay'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        min_pay = cleaned_data.get('min_pay')
        max_pay = cleaned_data.get('max_pay')
        
        # Validate salary range
        if min_pay and max_pay:
            if min_pay > max_pay:
                raise forms.ValidationError({
                    'max_pay': 'Maximum salary must be greater than or equal to minimum salary.'
                })
        
        return cleaned_data




# and we convert it to actual hours before saving to expires_at

class InviteLinkForm(forms.Form):
    expiry_duration = forms.ChoiceField(
        choices=EXPIRY_CHOICES,
        label='Link Expires In',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    max_uses = forms.IntegerField(
        required=False,       # optional — admin may not want a usage cap
        min_value=1,          # if they do set it, 0 makes no sense
        label='Usage Limit (Optional)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave blank for a default of 200'
        })
    )