from django.dispatch import receiver
from allauth.account.signals import user_signed_up

@receiver(user_signed_up)
def set_user_role_after_social_signup(sender, request, user, **kwargs):
    # This reads the 'user_role' you set in agent_google_login or company_google_login
    user_role = request.session.get('user_role')

    if user_role:
        # Update the user's role in the database
        user.role = user_role
        user.save()
        
        # Clean up the session so it doesn't interfere later
        del request.session['user_role']