from django import forms
from django.forms import ModelForm
from .models import *
from core.choices import STATES
from django.forms import formset_factory, inlineformset_factory
from django.core.exceptions import ValidationError

YES_NO_CHOICES=(
    (True, 'Yes'),
    (False, 'No')
)

class FeedbackForm(ModelForm):
    class Meta:
        model=Feedback
        fields=('feedback',)
        labels={'feedback': '',}
        widgets={'feedback': forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Please enter your feedback'}),}



#Form for putting properties up for sale
class LeaseForm(ModelForm):
    class Meta:
        model=PropertyManagementRent
        fields=(
                'house_type','description', 'state','location', 'owner', 'bedrooms','bathrooms','parking_spaces','size' ,
                'phone_number','price_range','base_image'
                )
        labels={
                'house_type':'House Type',
                'description': 'Property Description',
                'location': 'Precise Location',
                'owner': 'Listed by?',
                'price_range': 'Price',
                'phone_number': 'Phone Number',
                'state': 'State',
                'available': 'Visible To Public',
                'base_image': 'Add Overview image Of Property ',
}
        widgets= {
                    'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Property Description'}),
                    'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Oda Road, Kagola, Plot2,3'}),
                    'owner': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Company/Personal Name'}),
                    'price_range': forms.TextInput(attrs={'class': 'form-control'}),
                    'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                    # 'state': forms.ChoiceField(choices=[('', 'Any State')]+STATES, attrs={'class': 'form-control'}),
                    'available': forms.Select(choices=YES_NO_CHOICES,attrs={'class': 'form-control'}),
                    'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                    'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                    'parking_spaces':forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
                    'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Measured in square feet(sqft)'}),
}



#Form for putting properties up for sale
class SellForm(ModelForm):
    class Meta:
        model=PropertyManagementSale
        fields=('house_type','property_description', 'location', 'state','bathrooms','bedrooms','parking_spaces',
                'owner','phone_number','size', 'price','negotiate','available', 'base_image')
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
                    'parking_spaces':forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
                    'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Measured in square feet(sqft)'}),
}



class RentImageForm(ModelForm):
    class Meta:
        model= PropertyRentImage
        fields=('more_images', 'caption')
        widgets={
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image Description e.g Swimming Pool'})
        }


class SaleImageForm(ModelForm):
    class Meta:
        model= PropertySaleImage
        fields=('more_images', 'caption')
        widgets={
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image Description e.g Swimming Pool'})
        }

        


SaleImageFormSet= inlineformset_factory(
    PropertyManagementSale,
    PropertySaleImage,
    fields=('more_images', 'caption'),
    extra=3,
    max_num=3,
    can_delete=True,

)

RentImageFormSet= inlineformset_factory(
    PropertyManagementRent,
    PropertyRentImage,
    fields=('more_images', 'caption'),
    extra=3,
    max_num=3,
    can_delete=True,
)