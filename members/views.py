'''Handles the authentication Functionality'''

from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from .forms import RegistrationForm


#login View
def login_user(request):
    try:
        if request.method== "POST":
            #getting both the username and the password from the form filled 
            username= request.POST['username']
            password=request.POST['password']
            #Authenticate users based on the username and password 
            user= authenticate(request, username=username, password=password)#returns a bool 
            #If the user is found it then logs him/her in
            if user is not None:
                #logins user if the variable user is true
                login(request, user)
                messages.success(request, (f'Welcome Back {request.user.username}'))
                return redirect('user-profile')
            else:
                messages.error(request, ('Incorrect Credentials'))
                return redirect('login')
        else:
            return render(request, 'registration/login.html', {})
    except Exception as e:
        print(e)

#basically just logs out user
def logout_user(request):
    logout(request)
    messages.success(request, ('Thanks for stopping by I hope you found what you need'))
    return redirect("welcome-page")


#View/Function that handles the registration of users on the website using the registration form provided by django
def register_user(request):
    try:
        if request.method == 'POST':
            form= RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                #once the form is filled and submitted is clicked both the password and the usernames are checked if they meet the authentication requirement
                username= form.cleaned_data['username']
                password= form.cleaned_data['password1']
                #The user is then logged in after registration
                user= authenticate(username= username, password= password)
                login(request, user)
                messages.success(request, (f'Welcome {request.user.username}, and Thanks for joining Estate Web, Feel free to look around'))
                return redirect('user-profile')
            else:
                messages.error(request, ('Make Sure You filled all input boxes correctly'))
                return render(request, 'registration/register_user.html', {'form': form})
        else:
            #the form that needs to be filled
            form=RegistrationForm()
            return render(request, 'registration/register_user.html', {'form': form})
    except Exception as e:
        print(e)