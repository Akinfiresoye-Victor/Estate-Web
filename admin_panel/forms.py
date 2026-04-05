from django import forms
from django.contrib.auth import authenticate

class AdminLoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Username',
        'class': 'adm-input',
        'autocomplete': 'username',
        'required': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'adm-input',
        'autocomplete': 'current-password',
        'required': True
    }))

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
            
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None or not getattr(self.user_cache, 'is_staff', False) or not getattr(self.user_cache, 'is_superuser', False):
                # We do not distinguish between failing authentication and failing authorization
                # to prevent discovering existance of staff/superuser accounts.
                raise forms.ValidationError("Invalid credentials.")
        return cleaned_data
