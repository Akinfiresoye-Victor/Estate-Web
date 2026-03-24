'''Handles the authentication Functionality'''
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomerSignUpForm, CompanySignUpForm, AgentSignUpForm
from .models import User


# ─── login ────────────────────────────────────────────────────────────────────

def login_user(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user     = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome Back {request.user.username}')

                # next_url comes from the hidden field in the form (POST) or the
                # query string (GET) — both are checked.
                next_url = request.POST.get('next') or request.GET.get('next')

                if user.role == 'customer':
                    return redirect(next_url if next_url else 'customer:user-profile')
                elif user.role == 'agent':
                    return redirect(next_url if next_url else 'agent:dashboard')
                elif user.role == 'company':
                    return redirect(next_url if next_url else 'company:dashboard')
                else:
                    return redirect('landing')
            else:
                messages.error(request, 'Incorrect Credentials')
                return redirect('login')
        else:
            return render(request, 'registration/login.html', {})
    except Exception:
        print(e)


# ─── logout ───────────────────────────────────────────────────────────────────

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Thanks for stopping by. I hope you found what you need.')
        return redirect('landing')
    else:
        messages.error(request, 'You have to be logged in to perform that action')
        return redirect('login')


# ─── register_customer ────────────────────────────────────────────────────────

def register_customer(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = CustomerSignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user     = authenticate(username=username, password=password)
                login(request, user)
                messages.success(request, f'Welcome {request.user.username}, and Thanks for joining Estate Web!')

                # Honour next_url so new customers return to the page they came from
                next_url = request.POST.get('next') or request.GET.get('next')
                return redirect(next_url if next_url else 'customer:user-profile')
            else:
                messages.error(request, 'Make Sure You filled all input boxes correctly')
                return render(request, 'registration/register_customer.html', {'form': form, 'role': 'Customer'})
        else:
            form = CustomerSignUpForm()
            return render(request, 'registration/register_customer.html', {'form': form, 'role': 'Customer'})
    except Exception:
        print(e)


# ─── register_agent ───────────────────────────────────────────────────────────

def register_agent(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = AgentSignUpForm(request.POST)
            if form.is_valid():
                agent      = form.save(commit=False)
                agent.role = 'agent'
                agent.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user     = authenticate(username=username, password=password)
                login(request, user)
                messages.success(request, f'Welcome {request.user.username}, and Thanks for joining Estate Web!')
                next_url = request.POST.get('next') or request.GET.get('next')
                return redirect(next_url if next_url else 'agent:dashboard')
            else:
                messages.error(request, 'Make Sure You filled all input boxes correctly')
                return render(request, 'registration/register_agent.html', {'form': form, 'role': 'Agent'})
        else:
            form = AgentSignUpForm()
            return render(request, 'registration/register_agent.html', {'form': form, 'role': 'Agent'})
    except Exception:
        print(e)


# ─── register_company ─────────────────────────────────────────────────────────

def register_company(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = CompanySignUpForm(request.POST)
            if form.is_valid():
                company      = form.save(commit=False)
                company.role = 'company'
                company.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user     = authenticate(username=username, password=password)
                login(request, user)
                messages.success(request, f'Welcome {request.user.username}, and Thanks for joining Estate Web!')
                next_url = request.POST.get('next') or request.GET.get('next')
                return redirect(next_url if next_url else 'company:dashboard')
            else:
                messages.error(request, 'Make Sure You filled all input boxes correctly')
                return render(request, 'registration/register_company.html', {'form': form, 'role': 'Company'})
        else:
            form = CompanySignUpForm()
            return render(request, 'registration/register_company.html', {'form': form, 'role': 'Company'})
    except Exception:
        print(e)

