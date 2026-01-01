from django import forms
from django.forms import ModelForm
from .models import CompanyInformation, CompanySocialLinks
from core.choices import STATES
from django.forms import formset_factory, inlineformset_factory
from django.core.exceptions import ValidationError

# TODO add view property page to the update, appointment ets. section for companies
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


