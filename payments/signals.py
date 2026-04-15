# payments/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Subscription

DEFAULT_PLAN = {
    'company':  'starter',
    'agent':    'basic',
    'landlord': 'landlord_basic',
    'customer': 'standard',
}

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_subscription(sender, instance, created, **kwargs):
    if created:
        plan = DEFAULT_PLAN.get(instance.role, 'standard')
        Subscription.objects.create(user=instance, plan=plan)