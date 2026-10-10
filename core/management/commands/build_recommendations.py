import time
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import PropertyInteraction
from core.recommendations import recommendation_calculation, rebuild_all_recommendations


class Command(BaseCommand):
    help = 'Nightly job: refresh user taste, then score all properties for every user.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full', action='store_true',
            help='Recalculate taste for every user with history, not just recently active ones.',
        )
        parser.add_argument(
            '--pause', type=float, default=0.0,
            help='Seconds to rest between users (e.g. 0.05) to go easy on the database.',
        )

    def handle(self, *args, **options):
        started = time.monotonic()
        User = get_user_model()

        # Step 1: taste. Only users who acted recently, because taste only
        # changes when a user does something new.
        interactions = PropertyInteraction.objects.all()
        if not options['full']:
            interactions = interactions.filter(
                created_at__gte=timezone.now() - timedelta(hours=25)
            )
        active_ids = interactions.values('user_id').distinct()

        taste_done = taste_failed = 0
        for user in User.objects.filter(pk__in=active_ids).iterator():
            try:
                recommendation_calculation(user)
                taste_done += 1
            except Exception as e:
                taste_failed += 1
                self.stderr.write(f'Taste failed for user #{user.pk}: {e}')
            if options['pause']:
                time.sleep(options['pause'])
        self.stdout.write(f'Step 1: taste updated for {taste_done} user(s), {taste_failed} error(s).')

        # Step 2: scoring. Runs for EVERYONE with a taste profile, because new
        # listings appear every day even when the user did nothing.
        rebuilt, failed, cleared = rebuild_all_recommendations(pause=options['pause'])
        self.stdout.write(f'Step 2: {rebuilt} user(s) rebuilt, {failed} error(s), {cleared} stale row(s) cleared.')

        elapsed = time.monotonic() - started
        self.stdout.write(self.style.SUCCESS(f'Done in {elapsed:.1f}s.'))