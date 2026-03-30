from django import forms
from .models import LandlordInformation

class LandlordInformationForm(forms.ModelForm):
    class Meta:
        model = LandlordInformation
        fields = ['phone_number', 'location', 'profile_picture', 'government_id']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 08012345678'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'government_id': forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'government_id': 'Upload a clear photo of your ID (NIN, Driver\'s License, etc.) to help us verify you.',
        }
