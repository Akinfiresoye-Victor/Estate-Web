'''Contains all the forms used for authentication'''

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError



#form for registering users 
class RegistrationForm(UserCreationForm):
    first_name= forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name= forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email= forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model=User
        fields=('username', 'first_name', 'last_name','email', 'password1', 'password2') 
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class']= 'form-control'
        self.fields['password1'].widget.attrs['class']= 'form-control'
        self.fields['password2'].widget.attrs['class']= 'form-control'
        


#form for updating users profile and info
class UpdateUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=('username', 'first_name', 'last_name','email') 
    
    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


    #function to check if the username is valid 
    def clean_username(self):
        username = self.cleaned_data.get('username')
        #checking if the particular username used exists since one cant use the same username as others
        if User.objects.filter(username=username).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


    def clean_email(self):
        #Checking if the email was valid
        email = self.cleaned_data.get('email')
        #checking if the particular email used exists since one cant use the same email as others
        if User.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("This email is already registered.")
        return email



