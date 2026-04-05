# ─────────────────────────────────────────────────────────────────────────────
# management/commands/refresh_scores.py
#
# File location (create these folders if they don't exist):
#   core/
#     management/
#       __init__.py          ← empty file
#       commands/
#         __init__.py        ← empty file
#         refresh_scores.py  ← this file
#
# Run manually:
#   python manage.py refresh_scores
#
# Run daily with a cron job (Linux/server):
#   0 3 * * * cd /path/to/project && python manage.py refresh_scores
#   (runs at 3 AM every day)
#
# Or add to your hosting platform's task scheduler (Render, Railway, etc.)
# ─────────────────────────────────────────────────────────────────────────────

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from core.models import PropertyManagementSale, PropertyManagementRent
from core.utils import refresh_activity_score


class Command(BaseCommand):
    help = 'Recalculates listing scores for all active properties.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Bypass the 24-hour gate and refresh all properties immediately.',
        )

    def handle(self, *args, **options):
        force = options['force']
        now   = timezone.now()

        if force:
            # Bypass the gate: set last_reset_date to yesterday so
            # refresh_activity_score sees them all as stale.
            yesterday = now - timedelta(hours=25)
            PropertyManagementSale.objects.update(last_reset_date=yesterday)
            PropertyManagementRent.objects.update(last_reset_date=yesterday)
            self.stdout.write('Force flag set — all properties will be refreshed.')

        # ── Sale properties ───────────────────────────────────────────
        sale_qs = PropertyManagementSale.objects.all()
        to_update_sale = []
        sale_updated = 0
        sale_errors  = 0

        for prop in sale_qs:
            try:
                old_score = prop.listing_score
                new_score = refresh_activity_score(prop, 'Sale', save=False)
                if new_score != old_score:
                    sale_updated += 1
                to_update_sale.append(prop)
            except Exception as e:
                sale_errors += 1
                self.stderr.write(f'Error scoring Sale #{prop.pk}: {e}')
                continue

        if to_update_sale:
            PropertyManagementSale.objects.bulk_update(to_update_sale, ['listing_score', 'last_reset_date'])

        self.stdout.write(
            self.style.SUCCESS(
                f'Sale properties: {len(to_update_sale)} updated, '
                f'{sale_errors} errors.'
            )
        )

        # ── Rent properties ───────────────────────────────────────────
        rent_qs = PropertyManagementRent.objects.all()
        to_update_rent = []
        rent_updated = 0
        rent_errors  = 0

        for prop in rent_qs:
            try:
                old_score = prop.listing_score
                new_score = refresh_activity_score(prop, 'Rent', save=False)
                if new_score != old_score:
                    rent_updated += 1
                to_update_rent.append(prop)
            except Exception as e:
                rent_errors += 1
                self.stderr.write(f'Error scoring Rent #{prop.pk}: {e}')
                continue

        if to_update_rent:
            PropertyManagementRent.objects.bulk_update(to_update_rent, ['listing_score', 'last_reset_date'])

        self.stdout.write(
            self.style.SUCCESS(
                f'Rent properties: {len(to_update_rent)} updated, '
                f'{rent_errors} errors.'
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Done at {now.strftime("%Y-%m-%d %H:%M:%S")} UTC.'
            )
        )

