'''Contains all the form used all through the website except of authentication'''

from django import forms
from django.forms import ModelForm
from .models import LeadInfo
from companies.models import CompanyRating
from agents.models import AgentRating


class ReviewFormCompany(forms.ModelForm):
    class Meta:
        model = CompanyRating
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Review'
        }
        widgets = {
            'rating': forms.HiddenInput(attrs={'id': 'rating-value'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with this company...',
                'rows': 4,
                'required': True
            })
        }


class ReviewFormAgent(forms.ModelForm):
    class Meta:
        model = AgentRating
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Review'
        }
        widgets = {
            'rating': forms.HiddenInput(attrs={'id': 'rating-value'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with this company...',
                'rows': 4,
                'required': True
            })
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
            'schedule_tour': 'Schedule a date to view property Physically',
            'contact_type': 'Contact Media(How Should we contact you)'
        }
        widgets={
        'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'e.g johndoe@gmail.com'}),
        'inquiry_message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Intrested/Id like to know more about this'}),
        }






