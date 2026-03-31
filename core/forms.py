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
        model = Feedbacks
        fields = ('reaction', 'category', 'details', 'screenshot')
        # 'feedback' field removed — replaced by the new system fields above.
        # 'role' is not here because the view sets it programmatically,
        # not from direct user input on the form.
        # 'user' is not here for the same reason — the view links it
        # from request.user automatically.

        labels = {
            'reaction':   '',
            'category':   '',
            'details':    '',
            'screenshot': '',
        }

        widgets = {
            # reaction and category are handled by custom emoji/select UI
            # in the HTML — these hidden inputs just carry the values through.
            'reaction': forms.HiddenInput(),
            'category': forms.HiddenInput(),

            # details is the open text box
            'details': forms.Textarea(attrs={
                'class': 'fp-textarea',
                'placeholder': 'What happened? What would you like to see?',
                'rows': 4,
            }),

            # screenshot is a file input — shown only for bug reports
            'screenshot': forms.FileInput(attrs={
                'class': 'fp-screenshot-input',
                'accept': 'image/*',
            }),
        }


#Form for putting properties up for sale
class LeaseForm(ModelForm):
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

    class Meta:
        model=PropertyManagementRent
        fields=(
                'property_category','residential','commercial','lands','description', 'state','location', 'bedrooms','bathrooms','parking_spaces','size' ,
                'phone_number','price_range','base_image'
                )
        labels={
                'property_category': 'Property Category',
                'residential':'House Type',
                'description': 'Property Description',
                'location': 'Precise Location',
                'price_range': 'Price (per year)',
                'phone_number': 'Phone Number',
                'state': 'State',
                'base_image': 'Add Overview image Of Property ',
        }
        help_texts = {
            'price_range': 'Please enter the annual (yearly) rent amount. Tenants will see this as a yearly cost.',
        }
        widgets= {
                    'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Property Description'}),
                    'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Oda Road, Kagola, Plot2,3'}),
                    'price_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1,500,000'}),
                    'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                    'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                    'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                    'parking_spaces':forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
                    'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Measured in square feet(sqft)'}),
        }



#Form for putting properties up for sale
class SellForm(ModelForm):
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

    class Meta:
        model=PropertyManagementSale
        fields=('property_category','residential','commercial','lands','property_description', 'location', 'state','bathrooms','bedrooms','parking_spaces',
                'phone_number','size', 'price', 'base_image')
        labels={
                'property_category': 'Property Category',
                'residential':'House Type',
                'property_description': 'Property Description',
                'location': 'Location',
                'phone_number': 'Phone.No',
                'price': 'Price',
                'state': 'State',
                'base_image': 'Add Overview image Of Property ',
        }
        widgets= {
                    'property_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'E.g Spacious Family home with modern amenities'}),
                    'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g Akure,Oda road'}),
                    'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
                    'price': forms.TextInput(attrs={'class': 'form-control'}),
                    'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
                    'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
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





class PartnershipForm(forms.ModelForm):

    property_types = forms.ModelMultipleChoiceField(
        queryset=PropertyFocus.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Primary Property Focus',
    )

    partnership_benefits = forms.ModelMultipleChoiceField(
        queryset=PartnershipGoal.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Benefits You Are Most Interested In',
    )

    class Meta:
        model = Partnership
        fields = [
            'company_name', 'company_type', 'years_in_buisness', 'team_size',
            'company_website', 'city', 'state',
            'person_of_contact', 'person_position', 'email', 'phone_number',
            'average_listings', 'annual_revenue',
            'property_types', 'partnership_benefits',
            'growth_goals', 'why_question',
        ]
        widgets = {
            'company_name':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Okafor & Sons Properties'}),
            'company_type':      forms.Select(attrs={'class': 'form-control'}),
            'years_in_buisness': forms.Select(attrs={'class': 'form-control'}),
            'team_size':         forms.Select(attrs={'class': 'form-control'}),
            'company_website':   forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourcompany.com'}),
            'city':              forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lagos, Abuja'}),
            'state':             forms.Select(attrs={'class': 'form-control'}),
            'person_of_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full legal name'}),
            'person_position':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CEO, Director, Manager'}),
            'email':             forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@yourcompany.com'}),
            'phone_number':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0801 234 5678'}),
            'average_listings':  forms.Select(attrs={'class': 'form-control'}),
            'annual_revenue':    forms.Select(attrs={'class': 'form-control'}),
            'growth_goals':      forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key growth targets for the next 12 months...'}),
            'why_question':      forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us why you want to partner with Estate Web...'}),
        }
        labels = {
            'company_name':      'Company Name',
            'company_type':      'Type of Company',
            'years_in_buisness': 'Years in Business',
            'team_size':         'Team Size',
            'company_website':   'Company Website (Optional)',
            'city':              'Primary City',
            'state':             'State',
            'person_of_contact': 'Contact Person Full Name',
            'person_position':   'Their Position / Role',
            'email':             'Contact Email Address',
            'phone_number':      'Contact Phone Number',
            'average_listings':  'Average Monthly Listings',
            'annual_revenue':    'Estimated Annual Revenue',
            'growth_goals':      'Growth Goals for the Next 12 Months (Optional)',
            'why_question':      'Why Do You Want to Partner with Estate Web?',
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10 or len(digits) > 14:
            raise forms.ValidationError('Enter a valid Nigerian phone number.')
        return phone

    def clean_why_question(self):
        text = self.cleaned_data.get('why_question', '').strip()
        if len(text) < 30:
            raise forms.ValidationError('Please give us a bit more detail — at least 30 characters.')
        return text

