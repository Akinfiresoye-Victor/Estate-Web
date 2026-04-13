'''Handles the authentication Functionality'''
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomerSignUpForm, CompanySignUpForm, AgentSignUpForm, LandlordSignUpForm
from .models import User
from core.models import ErrorLog
import traceback
from django.utils.http import url_has_allowed_host_and_scheme
from typing import cast
from django.urls import reverse
from allauth.socialaccount.models import SocialLogin
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.models import EmailConfirmationHMAC
from core.ratelimit import ratelimit
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from core.utils import send_estate_email
import json
import threading
from allauth.account.internal.flows.email_verification import send_verification_email_to_address
from allauth.account.views import EmailView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required



@ratelimit(rate='5/m', key_prefix='login_protection')
def agent_google_login(request):
    # 1. Tag the session so we remember this is an Agent
    request.session['user_role'] = 'agent'

    # 2. Redirect to the actual Google login URL
    # This URL is usually '/accounts/google/login/'
    return redirect('/accounts/google/login/')

@ratelimit(rate='5/m', key_prefix='login_protection')
def company_google_login(request):
    # 1. Tag the session so we remember this is an Agent
    request.session['user_role'] = 'company'

    # 2. Redirect to the actual Google login URL
    # This URL is usually '/accounts/google/login/'
    return redirect('/accounts/google/login/')

@ratelimit(rate='5/m', key_prefix='login_protection')
def landlord_google_login(request):
    # 1. Tag the session so we remember this is a Landlord
    request.session['user_role'] = 'landlord'

    # 2. Redirect to the actual Google login URL
    return redirect('/accounts/google/login/')


@ratelimit(rate='5/m', key_prefix='login_protection')
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
                messages.success(request, f'Welcome back, {user.username}!')

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
                
                if request.user.role == 'customer':
                    return redirect('customer:user-profile')
                elif request.user.role == 'agent':
                    return redirect('agent:dashboard')
                elif request.user.role == 'landlord':
                    return redirect('landlord:dashboard')
                elif request.user.role == 'company':
                    return redirect('company:dashboard')
                else:
                    return redirect('landing')
            
            else:
                # Form contains specific errors if credentials don't match
                messages.error(request, 'Invalid username or password. Please try again.')
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
        messages.success(request, 'You have successfully logged out. See you soon!')
        return redirect('landing')
    else:
        messages.error(request, 'Please sign in to perform that action.')
        return redirect('login')


# ─── register_customer ───────────────────────────────────────────────────────
@ratelimit(rate='3/m', key_prefix='login_protection')
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
                    threading.Thread(
                        target=send_estate_email,
                        kwargs={
                            'subject': f'Welcome to Estate Web, {user.username}!',
                            'template_name': 'registration/welcome_email.html',
                            'context': {
                                'user': user,
                                'request': request
                            },
                            'recipient_list': [user.email]
                        },
                        daemon=True
                    ).start()
                    
                    messages.success(request, f'Welcome {user.username}! Check your email for onboarding info.')

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
                messages.error(request, 'Please correct the highlighted errors in the form.')
                return render(request, 'registration/register_customer.html', {'form': form, 'role': 'Customer'})
        else:
            form = CustomerSignUpForm()
            return render(request, 'registration/register_customer.html', {'form': form, 'role': 'Customer'})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


# ─── register_agent ───────────────────────────────────────────────────────────
@ratelimit(rate='3/m', key_prefix='login_protection')
def register_agent(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = AgentSignUpForm(request.POST)
            if form.is_valid():
                agent = form.save(commit=False)
                agent.role = 'agent'
                agent.save()
                
                
                email_address = EmailAddress.objects.create(
                    user=agent,
                    email=agent.email,
                    primary=True,
                    verified=False
                )
                confirmation = EmailConfirmationHMAC(email_address)
                threading.Thread(
                    target=get_adapter(request).send_confirmation_mail,
                    args=(request, confirmation),
                    kwargs={'signup': True},
                    daemon=True
                ).start()
                messages.success(request, 'Account created! Please check your email to verify your account.')
                threading.Thread(
                    target=send_estate_email,
                    kwargs={
                        'subject': f'Welcome to Estate Web, {agent.username}!',
                        'template_name': 'registration/welcome_email.html',
                        'context': {'user': agent, 'request': request},
                        'recipient_list': [agent.email]
                    },
                    daemon=True
                ).start()
                return redirect('account_email_verification_sent')
            else:
                messages.error(request, 'Please correct the highlighted errors in the form.')
                return render(request, 'registration/register_agent.html', {'form': form, 'role': 'Agent'})
        else:
            form = AgentSignUpForm()
            return render(request, 'registration/register_agent.html', {'form': form, 'role': 'Agent'})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


# ─── register_company ─────────────────────────────────────────────────────────
@ratelimit(rate='3/m', key_prefix='login_protection')
def register_company(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = CompanySignUpForm(request.POST)
            if form.is_valid():
                company = form.save(commit=False)
                company.role = 'company'
                company.save()
                
                # Send welcome email (Background)
                threading.Thread(
                    target=send_estate_email,
                    kwargs={
                        'subject': f'Welcome to Estate Web, {company.username}!',
                        'template_name': 'registration/welcome_email.html',
                        'context': {'user': company, 'request': request},
                        'recipient_list': [company.email]
                    },
                    daemon=True
                ).start()
                
                email_address = EmailAddress.objects.create(
                    user=company,
                    email=company.email,
                    primary=True,
                    verified=False
                )
                confirmation = EmailConfirmationHMAC(email_address)
                threading.Thread(
                    target=get_adapter(request).send_confirmation_mail,
                    args=(request, confirmation),
                    kwargs={'signup': True},
                    daemon=True
                ).start()
                messages.success(request, 'Account created! Please check your email to verify your account.')
                return redirect('account_email_verification_sent')
            else:
                messages.error(request, 'Please correct the highlighted errors in the form.')
                return render(request, 'registration/register_company.html', {'form': form, 'role': 'Company'})
        else:
            form = CompanySignUpForm()
            return render(request, 'registration/register_company.html', {'form': form, 'role': 'Company'})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


# ─── register_landlord ────────────────────────────────────────────────────────
@ratelimit(rate='3/m', key_prefix='login_protection')
def register_landlord(request):
    if request.user.is_authenticated:
        return redirect('landing')
    try:
        if request.method == 'POST':
            form = LandlordSignUpForm(request.POST)
            if form.is_valid():
                landlord = form.save(commit=False)
                landlord.role = 'landlord'
                landlord.save()
                
                # Send welcome email (Background)
                threading.Thread(
                    target=send_estate_email,
                    kwargs={
                        'subject': f'Welcome to Estate Web, {landlord.username}!',
                        'template_name': 'registration/welcome_email.html',
                        'context': {'user': landlord, 'request': request},
                        'recipient_list': [landlord.email]
                    },
                    daemon=True
                ).start()
                
                email_address = EmailAddress.objects.create(
                    user=landlord,
                    email=landlord.email,
                    primary=True,
                    verified=False
                )
                confirmation = EmailConfirmationHMAC(email_address)
                threading.Thread(
                    target=get_adapter(request).send_confirmation_mail,
                    args=(request, confirmation),
                    kwargs={'signup': True},
                    daemon=True
                ).start()   
                messages.success(request, 'Account created! Please check your email to verify your account.')
                return redirect('account_email_verification_sent')
            else:
                messages.error(request, 'Please correct the highlighted errors in the form.')
                return render(request, 'registration/register_landlord.html', {'form': form, 'role': 'Landlord'})
        else:
            form = LandlordSignUpForm()
            return render(request, 'registration/register_landlord.html', {'form': form, 'role': 'Landlord'})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})




@ratelimit(rate='3/h', key_prefix='email_reset')
def resend_verification(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        email_address = EmailAddress.objects.get(user=request.user, primary=True)
        confirmation = EmailConfirmationHMAC(email_address)
        if not email_address.verified:
            get_adapter(request).send_confirmation_mail(request, confirmation, signup=True)
            messages.success(request, "Verification email sent! Check your inbox.")
        else:
            messages.info(request, "Your email is already verified.")
            
    except EmailAddress.DoesNotExist:
        messages.error(request, "No email address found on your account.")
    
    return redirect('account_email')





@ratelimit(rate='3/h', key_prefix='email_reset')
class CustomEmailView(EmailView):
    success_url = reverse_lazy('account_email')

    def post(self, request, *args, **kwargs):
        # Only validate on action_add (the change email form)
        # action_send is the resend button — let that pass through normally
        if 'action_add' in request.POST:
            new_email = request.POST.get('email', '').strip().lower()

            if User.objects.filter(email__iexact=new_email).exists():
                messages.error(
                    request,
                    'That email address is already linked to an account. Please use a different one.'
                )
                return redirect('account_email')
            if new_email:
                EmailAddress.objects.filter(user=request.user).update(email=new_email,primary=True)
                User.objects.filter(id=request.user.id).update(email=new_email)
            else:
                messages.error(request, 'Invalid Request')
                return redirect('account_email')
        return super().post(request, *args, **kwargs)

@login_required
def logout_for_email_change(request):
    logout(request)
    return HttpResponseRedirect(
        reverse('login') + '?next=' + reverse('account_email')
    )
