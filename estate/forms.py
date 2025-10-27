'''Contains all the form used all through the website except of authentication'''

from django import forms
from django.forms import ModelForm
from .models import *
from .choices import STATES
from django.forms import formset_factory, inlineformset_factory
from django.core.exceptions import ValidationError



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
                'phone_number','price_range','base_image'
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
                'available', 'base_image')
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
                    'parking_spaces':forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
}



class FeedbackForm(ModelForm):
    class Meta:
        model=Feedback
        fields=('feedback',)
        labels={'feedback': '',}
        widgets={'feedback': forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Please enter your feedback'}),}



class UserInformationForm(forms.ModelForm):
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


class AgentInformationForm(forms.ModelForm):
    class Meta:
        model = Agent_Information
        fields = ['professional_title', 'professional_introduction', 'call_to_action']
        labels={
            'professional_title': '',
            'professional_Introduction': 'Quick Summary potential client will read',
            'call_to_action': ''
        }
        widgets={'professional_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Realtor, Property Consultant'}),
                'professional_introduction': forms.Textarea(attrs={'class': 'form-control'}),
                'call_to_action': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g Lets Discuss your home-buying goals'})}





class ExperienceForm(forms.ModelForm):
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


class RentImageForm(forms.ModelForm):
    class Meta:
        model= PropertyRentImage
        fields=('more_images', 'caption')
        widgets={
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image Description e.g Swimming Pool'})
        }


class SaleImageForm(forms.ModelForm):
    class Meta:
        model= PropertySaleImage
        fields=('more_images', 'caption')
        widgets={
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image Description e.g Swimming Pool'})
        }

        
'''formset'''
ExperienceFormSet = inlineformset_factory(
    Agent_Information, 
    Experience,        
    form= ExperienceForm,
    extra=1,
    can_delete=True,
    
)

SocialLinksFormSet= inlineformset_factory(
    Agent_Information,
    SocialLinks,
    fields=('social_platform', 'link_to_social'),
    extra=1,
    can_delete=True
)

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