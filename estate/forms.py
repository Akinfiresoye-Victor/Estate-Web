'''Contains all the form used all through the website except of authentication'''

from django import forms
from django.forms import ModelForm
from .models import *
from core.choices import STATES
from django.forms import formset_factory, inlineformset_factory
from django.core.exceptions import ValidationError













class UserInformationForm(ModelForm):
    class Meta:
        model = UserInformation
        fields = ['first_name', 'last_name', 'phone_number', 'email']
        labels={
            'first_name': '',
            'last_name': '',
            'phone_number': 'Company/Personal Contact Number',
            'email': 'Company/Personal Email'
        }
        widgets={'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Adeola'}),
                'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Victor'}),
                }







class InquiryForm(ModelForm):
    class Meta:
        model= LeadInfo
        fields=['name', 'email', 'phone_no','inquiry_message', 'contact_type','schedule_tour']
        labels={
            'name': 'Name',
            'email': 'Email',
            'phone_no': 'Whatsapp Phone Number',
            'inquiry_message': 'Book this property(send an inquiry message)',
            'schedule_tour': 'Schedule a date to view property Physically(optional)',
            'contact_type': 'Contact Media(How Should we contact you)'
        }
        widgets={
        'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'e.g johndoe@gmail.com'}),
        'inquiry_message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Intrested/Id like to know more about this'}),
        }






