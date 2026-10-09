from celery import shared_task
from django.contrib.auth import get_user_model

from .recommendations import recommendation_calculation


@shared_task
def recalculate_all_recommendations():
    User = get_user_model()
    # Only users who have at least one interaction
    users = User.objects.filter(property_interactions__isnull=False).distinct()

    count = 0
    for user in users.iterator():   # iterator() loads users one at a time, saving memory
        recommendation_calculation(user)
        count += 1
    return count