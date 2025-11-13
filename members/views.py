'''Handles the authentication Functionality'''
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from .forms import CustomerSignUpForm, CompanySignUpForm, AgentSignUpForm
from .models import User






#login View
def login_user(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method== "POST":
            #getting both the username and the password from the form filled 
            username= request.POST['username']
            password=request.POST['password']
            #Authenticate users based on the username and password 
            user= authenticate(request, username=username, password=password)#returns a bool 
            #If the user is found it then logs him/her in
            if user is not None:
                print('Found')
                #logins user if the variable user is true
                login(request, user)
                messages.success(request, (f'Welcome Back {request.user.username}'))
                print(request.user.role)
                if user.role == 'customer':
                    return redirect('customer:user-profile')
                elif user.role == 'agent':
                    return redirect('agent:dashboard')
                elif user.role == 'company':
                    print('company_dashboard')
                    return redirect('company:dashboard')
                else:
                    print('landing page')
                    return redirect('landing')
            else:
                messages.error(request, ('Incorrect Credentials'))
                return redirect('login')
        else:
            return render(request, 'registration/login.html', {})
    except Exception as e:
        print(e)

#basically just logs out user
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, ('Thanks for stopping by I hope you found what you need'))
        return redirect("landing")
    else:
        messages.error(request, 'You have to be logged in to perform that action')
        return redirect('login')


#View/Function that handles the registration of users on the website using the registration form provided by django
def register_customer(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form= CustomerSignUpForm(request.POST)
            if form.is_valid():
                form.save()
                #once the form is filled and submitted is clicked both the password and the usernames are checked if they meet the authentication requirement
                username= form.cleaned_data['username']
                password= form.cleaned_data['password1']
                #The user is then logged in after registration
                user= authenticate(username= username, password= password)
                login(request, user)
                messages.success(request, (f'Welcome {request.user.username}, and Thanks for joining Estate Web, Feel free to look around'))
                return redirect('customer:user-profile')
            else:
                messages.error(request, ('Make Sure You filled all input boxes correctly'))
                return render(request, 'registration/register_customer.html', {'form': form, 'role':'Customer'})
        else:
            #the form that needs to be filled
            form=CustomerSignUpForm()
            return render(request, 'registration/register_customer.html', {'form': form, 'role':'Customer'})
    except Exception as e:
        print(e)


def register_agent(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form= AgentSignUpForm(request.POST)
            if form.is_valid():
                agent=form.save(commit=False)
                agent.role='agent'
                agent.save()
                #once the form is filled and submitted is clicked both the password and the usernames are checked if they meet the authentication requirement
                username= form.cleaned_data['username']
                password= form.cleaned_data['password1']
                #The user is then logged in after registration
                user= authenticate(username= username, password= password)
                login(request, user)
                messages.success(request, (f'Welcome {request.user.username}, and Thanks for joining Estate Web, Feel free to look around'))
                return redirect('agent:agent_dashboard')
            else:
                messages.error(request, ('Make Sure You filled all input boxes correctly'))
                return render(request, 'registration/register_agent.html', {'form': form, 'role':'Agent'})
        else:
            #the form that needs to be filled
            form=AgentSignUpForm()
            return render(request, 'registration/register_agent.html', {'form': form, 'role':'Agent'})
    except Exception as e:
        print(e)


def register_company(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form= CompanySignUpForm(request.POST)
            if form.is_valid():
                company=form.save(commit=False)
                company.role = 'company'
                company.save()
                #once the form is filled and submitted is clicked both the password and the usernames are checked if they meet the authentication requirement
                username= form.cleaned_data['username']
                password= form.cleaned_data['password1']
                #The user is then logged in after registration
                user= authenticate(username= username, password= password)
                login(request, user)
                messages.success(request, (f'Welcome {request.user.username}, and Thanks for joining Estate Web, Feel free to look around'))
                return redirect('company:dashboard')
            else:
                messages.error(request, ('Make Sure You filled all input boxes correctly'))
                return render(request, 'registration/register_company.html', {'form': form, 'role':'Company'})
        else:
            #the form that needs to be filled
            form=CompanySignUpForm()
            return render(request, 'registration/register_company.html', {'form': form, 'role':'Company'})
    except Exception as e:
        print(e)