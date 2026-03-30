from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(user_logged_in)
def notify_admin_login(sender, request, user, **kwargs):
    if not user.is_staff: # Only notify if an admin/staff logs in
        send_mail(
            subject="⚠️ Security Alert: Admin Login",
            message=f"Admin user {user.username} has logged into the estate portal.",
            from_email="contact@estatewebng.com",
            recipient_list=["contact@estatewebng.com"],
        )