from django.dispatch import receiver
from allauth.account.signals import user_signed_up, email_confirmed
from allauth.account.models import EmailAddress
import threading
from core.utils import send_estate_email


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


@receiver(email_confirmed)
def set_new_primary_email(sender, request, email_address, **kwargs):
    """
    Fires automatically when a user clicks a verification link.
    Swaps the newly verified email to primary and updates user.email.
    """
    user = email_address.user

    # 1. Demote all other email addresses to non-primary
    EmailAddress.objects.filter(user=user).exclude(pk=email_address.pk).update(primary=False)

    # 2. Make the newly verified one the primary
    email_address.primary = True
    email_address.save()

    # 3. Update the actual user.email field to match
    user.email = email_address.email
    user.save(update_fields=['email'])