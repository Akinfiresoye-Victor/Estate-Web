from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.role == 'agent':
            return resolve_url('agent:dashboard')
        elif user.role == 'company':
            return resolve_url('company:dashboard')
        return resolve_url('customer:user-profile')