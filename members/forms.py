'''Contains all the forms used for authentication'''

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError



#form for registering users 
class RegistrationForm(UserCreationForm):
    first_name= forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control','placeholder': 'First Name'}), label='')
    
    last_name= forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}), label='')
    
    username= forms.CharField(max_length=20, widget=forms.TextInput(
        attrs= {'class': 'form-control', 'placeholder': 'Username'}), label='', help_text='')
    
    password1= forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Password'}), help_text='', label='')
    
    password2= forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),help_text='', label='')
    
    class Meta:
        model=User
        fields=('username', 'first_name', 'last_name', 'password1', 'password2') 


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



