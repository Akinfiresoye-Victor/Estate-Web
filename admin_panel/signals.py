from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from core.utils import send_estate_email

@receiver(user_logged_in)
def notify_admin_login(sender, request, user, **kwargs):
    if user.is_staff:  # Only notify for actual staff/admin logins
        try:
            send_estate_email(
                subject="\u26a0\ufe0f Security Alert: Admin Login",
                template_name='emails/admin_login_alert.html',
                context={
                    'username': user.username,
                    'ip': request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown')),
                    'request': request,
                },
                recipient_list=['contact@estatewebng.com'],
            )
        except Exception:
            pass  # Never let a notification email crash the login flow