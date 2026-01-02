from django import forms
from django.forms import ModelForm
from .models import *
from core.choices import APPOINTMENT_TYPE
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
                'property_category','residential','commercial','lands','description', 'state','location', 'bedrooms','bathrooms','parking_spaces','size' ,
                'phone_number','price_range','base_image'
                )
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # Add CSS classes to fields
            self.fields['property_category'].widget.attrs.update({
                'class': 'form-input',
                'id': 'property_category'
            })
            self.fields['residential'].widget.attrs.update({
                'class': 'form-input property-type-field',
                'id': 'residential'
            })
            self.fields['commercial'].widget.attrs.update({
                'class': 'form-input property-type-field',
                'id': 'commercial'
            })
            self.fields['lands'].widget.attrs.update({
                'class': 'form-input property-type-field',
                'id': 'lands'
            })
        labels={
                'property_category': 'Property Category',
                'residential':'House Type',
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
        fields=('property_category','residential','commercial','lands','property_description', 'location', 'state','bathrooms','bedrooms','parking_spaces',
                'phone_number','size', 'price','available', 'base_image')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # Add CSS classes to fields
            self.fields['property_category'].widget.attrs.update({
                'class': 'form-input',
                'id': 'property_category'
            })
            self.fields['residential'].widget.attrs.update({
                'class': 'form-input property-type-field',
                'id': 'residential'
            })
            self.fields['commercial'].widget.attrs.update({
                'class': 'form-input property-type-field',
                'id': 'commercial'
            })
            self.fields['lands'].widget.attrs.update({
                'class': 'form-input property-type-field',
                'id': 'lands'
            })
        labels={
                'property_category': 'Property Category',
                'residential':'House Type',
                'property_description': 'Property Description',
                'location': 'Location',
                'phone_number': 'Phone.No',
                'price': 'Price',
                'state': 'State',
                'available': 'Visible To Public',
                'base_image': 'Add Overview image Of Property ',
}
        widgets= {
                    'property_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'E.g Spacious Family home with modern amenities'}),
                    'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Akure,Oda road'}),
                    'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                    'price': forms.TextInput(attrs={'class': 'form-control'}),
                    # 'state': forms.ChoiceField(attrs={'class': 'form-control'}),
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


class AppointmentForm(ModelForm):
    class Meta:
        model = Appointments
        fields = ('appointment', 'note', 'appointment_type')
        
        widgets = {
            'appointment': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-input',
                    'placeholder': 'Select appointment date',
                    'required': True
                }
            ),
            'note': forms.Textarea(
                attrs={
                    'class': 'form-textarea',
                    'placeholder': 'Enter appointment notes or details...',
                    'rows': 4,
                    'maxlength': 500
                }
            ),
            'appointment_type': forms.Select(
                attrs={
                    'class': 'form-select',
                    'required': True
                }
            ),
        }
        
        labels = {
            'appointment': 'Appointment Date',
            'note': 'Appointment Notes',
            'appointment_type': 'Appointment Type',
        }
        
        help_texts = {
            'appointment': 'Select the date for this appointment',
            'note': 'Add any relevant notes or details about this appointment',
            'appointment_type': 'Choose the type of appointment',
        }
    
    def clean_appointment(self):
        appointment_date = self.cleaned_data.get('appointment')
        from django.utils import timezone
        
        # Ensure appointment is not in the past
        if appointment_date and appointment_date < timezone.now().date():
            raise forms.ValidationError('Appointment date cannot be in the past.')
        
        return appointment_date
    
    def clean_note(self):
        note = self.cleaned_data.get('note')
        
        # Provide default if empty
        if not note or note.strip() == '':
            return 'No Note Provided'
        
        return note.strip()