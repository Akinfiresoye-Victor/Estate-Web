'''Contains all the form used all through the website except of authentication'''

from django import forms
from django.forms import ModelForm
from .models import PropertyManagementRent, PropertyManagementSale
from .choices import STATES



YES_NO_CHOICES=(
    (True, 'Yes'),
    (False, 'No')
)



#Form for putting properties up for sale
class LeaseForm(ModelForm):
    class Meta:
        model=PropertyManagementRent
        fields=(
                'description', 'location', 'price_range', 'phone_number','state', 'summary', 'available', 'bedrooms',
                'bathrooms','base_image', 'image1', 'image2', 'image3', 'image4', 'image5', 'image6' 
                )
        labels={'description': 'Property Description',
                'location': 'Precise Location',
                'price_range': 'Price',
                'phone_number': 'Phone Number',
                'state': 'State',
                'summary': 'Short Description',
                'available': 'Visible To Public',
                'base_image': 'Add Overview image Of Property ',
                'image1': 'Add more images',
                'image2': '',
                'image3': '',
                'image4': '',
                'image5':'',
                'image6': ''
                # 'available': 'Is Property Available?'
                
}
        widgets= {'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Property Description'}),
                    'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Oda Road, Kagola, Plot2,3'}),
                    'price_range': forms.TextInput(attrs={'class': 'form-control'}),
                    'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                    # 'state': forms.ChoiceField(choices=[('', 'Any State')]+STATES, attrs={'class': 'form-control'}),
                    'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g 2 Bedroom Flat, Penthouse'}),
                    'available': forms.Select(choices=YES_NO_CHOICES,attrs={'class': 'form-control'}),
                    'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                    'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
}





#Form for putting properties up for sale
class SellForm(ModelForm):
    class Meta:
        model=PropertyManagementSale
        fields=('property_description', 'location', 'phone_number', 'price', 'owner','state','summary','negotiate', 'available', 'base_image', 'image1', 'image2', 'image3', 'image4', 'image5', 'image6' )
        labels={'property_description': 'Property Description',
                'location': 'Location',
                'phone_number': 'Phone.No',
                'price': 'Price',
                'owner':'Listed By?',
                'state': 'State',
                'summary': 'Short Description',
                'negotiate': 'Is it Negotiatable?',
                'available': 'Visible To Public',
                'base_image': 'Add Overview image Of Property ',
                'image1': 'Add more images',
                'image2': '',
                'image3': '',   
                'image4': '',
                'image5':'',
                'image6': ''
}
        widgets= {'property_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'E.g Spacious Family home with modern amenities'}),
                    'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Akure,Oda road'}),
                    'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                    'price': forms.TextInput(attrs={'class': 'form-control'}),
                    'owner': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Company/Personal Name'}),
                    # 'state': forms.ChoiceField(attrs={'class': 'form-control'}),
                    'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Penthouse'}),
                    'negotiate': forms.Select(attrs={'class': 'form-control'}),
                    'available': forms.Select(choices=YES_NO_CHOICES,attrs={'class': 'form-control'}),
}
