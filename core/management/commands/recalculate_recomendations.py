from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.recommendations import recommendation_calculation


class Command(BaseCommand):
    help = 'Recalculates recommendation data (Sale and Rent) for users with interactions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Only recalculate for this one user (useful for testing).',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        user_id = options['user_id']

        if user_id:
            try:
                users = User.objects.filter(pk=user_id)
                if not users.exists():
                    raise CommandError(f'No user found with id {user_id}.')
            except ValueError:
                raise CommandError('User id must be a number.')
        else:
            # Only users who have at least one interaction
            users = (
                User.objects
                .filter(property_interactions__isnull=False)
                .distinct()
            )

        count = 0
        errors = 0

        for user in users.iterator():
            try:
                recommendation_calculation(user)
                count += 1
            except Exception as e:
                errors += 1
                self.stderr.write(f'Error for user #{user.pk}: {e}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Recommendations updated for {count} user(s), {errors} error(s).'
            )
        )