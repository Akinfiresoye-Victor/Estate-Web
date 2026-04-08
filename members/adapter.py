from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from core.utils import send_estate_email


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.role == 'agent':
            return resolve_url('agent:dashboard')
        elif user.role == 'company':
            return resolve_url('company:dashboard')
        elif user.role == 'landlord':
            return resolve_url('landlord:dashboard')
        return resolve_url('customer:user-profile')



class MyAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        """
        Overrides the default send_mail to use our premium send_estate_email utility.
        This ensures all allauth emails (confirmation, reset) look professional.
        """
        
        # allauth provides template_prefix e.g. "account/email/email_confirmation"
        # We append .html to use our new templates
        subject_template = f"{template_prefix}_subject.txt"
        
        # 1. Render subject (always text)
        from django.template.loader import render_to_string
        subject = render_to_string(subject_template, context).strip()
        
        # 2. Use our utility for the Body (HTML + Text fallback)
        # We use prefix + "_message.html"
        html_template = f"{template_prefix}_message.html"
        
        # Send via our utiliy
        send_estate_email(
            subject=subject,
            template_name=html_template,
            context=context,
            recipient_list=[email]
        )
    def is_email_verification_required(self, request, email):
        """
        Logic to decide if verification is needed.
        """
        # You can access the session we set in the views.py
        user_role = request.session.get('user_role')
        
        
        if user_role in ['agent', 'company', 'landlord']:
            return True
            
        return False
    def get_email_confirmation_url(self, request, emailconfirmation):
        # This controls the link inside the verification email itself
        return super().get_email_confirmation_url(request, emailconfirmation)