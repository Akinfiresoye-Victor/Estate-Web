# payments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

PLAN_LIMITS = {
    # company
    'starter':       {'inventory_slots': 10,  'listing_slots': 8,   'boost_credits': 0},
    'growth':        {'inventory_slots': 100, 'listing_slots': 55,  'boost_credits': 3},
    'enterprise':    {'inventory_slots': None, 'listing_slots': None,'boost_credits': 10},
    # agent
    'basic':         {'inventory_slots': 5,   'listing_slots': 3,   'boost_credits': 0},
    'active_agent':  {'inventory_slots': 30,  'listing_slots': 15,  'boost_credits': 1},
    'top_producer':  {'inventory_slots': 100, 'listing_slots': 40,  'boost_credits': 4},
    # landlord
    'landlord_basic':{'inventory_slots': 3,   'listing_slots': 2,   'boost_credits': 0},
    'landlord_pro':  {'inventory_slots': 7, 'listing_slots': 6,'boost_credits': 2},
    # customer
    'standard':      {'wishlist_slots': 5,    'compare_slots': 2},
    'vip_hunter':    {'wishlist_slots': None,  'compare_slots': 6},
}

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('growth', 'Growth'),
        ('enterprise', 'Enterprise'),
        ('basic', 'Basic'),
        ('active_agent', 'Active Agent'),
        ('top_producer', 'Top Producer'),
        ('landlord_basic', 'Landlord Basic'),
        ('landlord_pro', 'Landlord Pro'),
        ('standard', 'Standard'),
        ('vip_hunter', 'VIP Hunter'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.CharField(max_length=30, choices=PLAN_CHOICES, default='starter')
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    paystack_reference = models.CharField(max_length=100, blank=True)

    def get_limit(self, key):
        """
        Call this anywhere to get a plan limit.
        Returns None means unlimited.
        Example: request.user.subscription.get_limit('inventory_slots')
        """
        limits = PLAN_LIMITS.get(self.plan, {})
        return limits.get(key, 0)

    def is_expired(self):
        if self.expiry_date is None:
            return False  # free plans never expire
        return timezone.now() > self.expiry_date

    def __str__(self):
        return f"{self.user} — {self.plan}"