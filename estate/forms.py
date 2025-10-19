'''Contains all the form used all through the website except of authentication'''

from django import forms
from django.forms import ModelForm
from .models import PropertyManagementRent, PropertyManagementSale, Feedback
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
                'house_type','description', 'state','location', 'bedrooms','bathrooms','parking_spaces', 
                'phone_number','price_range','base_image', 'image1', 'image2', 'image3', 'image4', 'image5', 'image6',  'available', 
                )
        labels={
                'house_type':'House Type',
                'description': 'Property Description',
                'location': 'Precise Location',
                'price_range': 'Price',
                'phone_number': 'Phone Number',
                'state': 'State',
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
        widgets= {
                    'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Property Description'}),
                    'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Oda Road, Kagola, Plot2,3'}),
                    'price_range': forms.TextInput(attrs={'class': 'form-control'}),
                    'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                    # 'state': forms.ChoiceField(choices=[('', 'Any State')]+STATES, attrs={'class': 'form-control'}),
                    'available': forms.Select(choices=YES_NO_CHOICES,attrs={'class': 'form-control'}),
                    'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                    'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                    'parking_spaces':forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
}





#Form for putting properties up for sale
class SellForm(ModelForm):
    class Meta:
        model=PropertyManagementSale
        fields=('house_type','property_description', 'location', 'state','bathrooms','bedrooms','parking_spaces','owner','phone_number', 'price','negotiate',
                'available', 'base_image', 'image1', 'image2', 'image3', 'image4', 'image5', 'image6' )
        labels={
                'house_type':'House Type',
                'property_description': 'Property Description',
                'location': 'Location',
                'phone_number': 'Phone.No',
                'price': 'Price',
                'owner':'Listed By?',
                'state': 'State',
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
        widgets= {
                    'property_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'E.g Spacious Family home with modern amenities'}),
                    'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Akure,Oda road'}),
                    'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                    'price': forms.TextInput(attrs={'class': 'form-control'}),
                    'owner': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Company/Personal Name'}),
                    # 'state': forms.ChoiceField(attrs={'class': 'form-control'}),
                    'negotiate': forms.Select(attrs={'class': 'form-control'}),
                    'available': forms.Select(choices=YES_NO_CHOICES,attrs={'class': 'form-control'}),
                    'parking_spaces':forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
}


class FeedbackForm(ModelForm):
    class Meta:
        model=Feedback
        fields=('feedback',)
        labels={'feedback': '',}
        widgets={'feedback': forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Please enter your feedback'}),}