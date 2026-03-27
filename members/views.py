'''Handles the authentication Functionality'''
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomerSignUpForm, CompanySignUpForm, AgentSignUpForm
from .models import User
from core.models import ErrorLog
import traceback
from django.utils.http import url_has_allowed_host_and_scheme
from typing import cast

# ─── login ────────────────────────────────────────────────────────────────────



def login_user(request):
    # 1. Guard clause for already logged-in users
    if request.user.is_authenticated:
        return redirect('landing')

    try:
        if request.method == "POST":
            # 2. Use the built-in form to validate and sanitize data
            form = AuthenticationForm(request, data=request.POST)
            
            if form.is_valid():
                user = cast(User, form.get_user())
                login(request, user)
                messages.success(request, f'Welcome Back {user.username}')

                # 3. Secure the 'next' redirect URL
                next_url = request.POST.get('next') or request.GET.get('next')
                
                # Check if the URL is safe (prevents hackers from redirecting users away from your site)
                is_safe = url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ) if next_url else False

                # 4. Role-based Redirection
                if is_safe:
                    return redirect(next_url)
                
                if user.role == 'customer':
                    return redirect('customer:user-profile')
                elif user.role == 'agent':
                    return redirect('agent:dashboard')
                elif user.role == 'company':
                    return redirect('company:dashboard')
                else:
                    return redirect('landing')
            
            else:
                # Form contains specific errors if credentials don't match
                messages.error(request, 'Incorrect Credentials')
                return redirect('login')    
        else:
            # Handle GET request
            form = AuthenticationForm()

        return render(request, 'registration/login.html', {'form': form})

    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



# ─── logout ───────────────────────────────────────────────────────────────────

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Thanks for stopping by. I hope you found what you need.')
        return redirect('landing')
    else:
        messages.error(request, 'You have to be logged in to perform that action')
        return redirect('login')


# ─── register_customer ───────────────────────────────────────────────────────

def register_customer(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = CustomerSignUpForm(request.POST)
            if form.is_valid():
                user = form.save() # Usually save() returns the user object
                username = form.cleaned_data['username']
                password = form.cleaned_data.get('password1')
                
                # Authenticate and Login
                user = cast(User, authenticate(request, username=username, password=password))
                if user:
                    login(request, user)
                    messages.success(request, f'Welcome {user.username}, and Thanks for joining Estate Web!')

                # --- START SECURITY FIX ---
                next_url = request.POST.get('next') or request.GET.get('next')
                
                # Validate the URL is safe and belongs to your site
                is_safe = url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ) if next_url else False

                # Redirect to the safe URL, or the profile if unsafe/missing
                return redirect(next_url if is_safe else 'customer:user-profile')
                # --- END SECURITY FIX ---

            else:
                messages.error(request, 'Make Sure You filled all input boxes correctly')
                return render(request, 'registration/register_customer.html', {'form': form, 'role': 'Customer'})
        else:
            form = CustomerSignUpForm()
            return render(request, 'registration/register_customer.html', {'form': form, 'role': 'Customer'})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


# ─── register_agent ───────────────────────────────────────────────────────────
def register_agent(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = AgentSignUpForm(request.POST)
            if form.is_valid():
                # Save the new agent and assign the role
                agent = form.save(commit=False)
                agent.role = 'agent'
                agent.save()
                
                username = form.cleaned_data['username']
                password = form.cleaned_data.get('password1')
                
                # Authenticate and Login the new agent
                user = cast(User, authenticate(request, username=username, password=password))
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome {user.username}, and Thanks for joining Estate Web!')

                # --- START SECURITY FIX ---
                next_url = request.POST.get('next') or request.GET.get('next')
                
                # Check if the URL is safe and belongs to your site (Lagos/Estate Web domain)
                is_safe = url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ) if next_url else False

                # Redirect to the 'next' page only if it's safe; otherwise, go to agent dashboard
                return redirect(next_url if is_safe else 'agent:dashboard')
                # --- END SECURITY FIX ---

            else:
                messages.error(request, 'Make Sure You filled all input boxes correctly')
                return render(request, 'registration/register_agent.html', {'form': form, 'role': 'Agent'})
        else:
            form = AgentSignUpForm()
            return render(request, 'registration/register_agent.html', {'form': form, 'role': 'Agent'})
            
    except Exception:
        # Using your existing ErrorLog model for tracking
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


# ─── register_company ─────────────────────────────────────────────────────────

def register_company(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = CompanySignUpForm(request.POST)
            if form.is_valid():
                # Save the user and set role to company
                company = form.save(commit=False)
                company.role = 'company'
                company.save()
                
                username = form.cleaned_data['username']
                password = form.cleaned_data.get('password1')
                
                # Log the new company user in immediately
                user = cast(User, authenticate(request, username=username, password=password))
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome {user.username}, and Thanks for joining Estate Web!')

                # --- START SECURITY FIX ---
                next_url = request.POST.get('next') or request.GET.get('next')
                
                # Check if the URL is safe and belongs to your domain
                is_safe = url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ) if next_url else False

                # Redirect to the 'next' URL if safe, otherwise to company dashboard
                return redirect(next_url if is_safe else 'company:dashboard')
                # --- END SECURITY FIX ---

            else:
                messages.error(request, 'Make Sure You filled all input boxes correctly')
                return render(request, 'registration/register_company.html', {'form': form, 'role': 'Company'})
        else:
            form = CompanySignUpForm()
            return render(request, 'registration/register_company.html', {'form': form, 'role': 'Company'})
            
    except Exception:
        # Log any system crashes using your ErrorLog model
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
