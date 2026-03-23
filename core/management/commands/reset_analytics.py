# ─────────────────────────────────────────────────────────────────────────────
# management/commands/reset_analytics.py
#
# Runs the 30-day analytics reset for all companies.
# Fires the same logic that was previously triggered on page load,
# but now runs on a schedule so it works even if nobody visits the page.
#
# Run manually:
#   python manage.py reset_analytics
#
# Schedule on Render (separate cron job from refresh_scores):
#   0 2 * * * cd /path/to/project && python manage.py reset_analytics
#   (runs at 2 AM every day — offset from refresh_scores which runs at 3 AM)
# ─────────────────────────────────────────────────────────────────────────────

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from companies.models import CompanyAnalytics, CompanyInformation
from core.models import PropertyViews, SessionId


class Command(BaseCommand):
    help = 'Resets 30-day analytics counters for companies whose window has expired.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset all companies immediately, ignoring the 30-day gate.',
        )

    def handle(self, *args, **options):
        force       = options['force']
        now         = timezone.now()
        reset_count = 0
        skip_count  = 0

        # Fetch all analytics rows with their company in one query
        all_analytics = CompanyAnalytics.objects.select_related('company').all()

        for analytics in all_analytics:
            company        = analytics.company
            time_difference = now - analytics.last_reset_date

            # Check if 30 days have passed — or force flag is set
            if force or time_difference >= timedelta(days=30):

                # ── Rolling averages ─────────────────────────────────────────
                # Formula: (last_month + running_average) // 2
                # This keeps the average from being skewed by one unusually
                # good or bad month — it smooths out over time.
                analytics.average_profile_views = (
                    analytics.profile_views + analytics.average_profile_views
                ) // 2
                analytics.average_lease_views = (
                    analytics.property_views_l + analytics.average_lease_views
                ) // 2
                analytics.average_sale_views = (
                    analytics.property_views_s + analytics.average_sale_views
                ) // 2
                analytics.average_leads = (
                    analytics.monthly_leads + analytics.average_leads
                ) // 2
                analytics.average_reviews = (
                    analytics.monthly_reviews + analytics.average_reviews
                ) // 2

                # ── Reset current month counters to 0 ────────────────────────
                # The averages above are the permanent record.
                # These counters start fresh for the new window.
                analytics.profile_views    = 0
                analytics.property_views_l = 0
                analytics.property_views_s = 0
                analytics.monthly_leads    = 0
                analytics.monthly_reviews  = 0

                # ── Move the window forward ──────────────────────────────────
                # This is the key line — last_reset_date becomes the new
                # window_start. Every date-filtered query in the views uses
                # this field as its __gte filter, so they automatically
                # start counting from this point forward.
                analytics.last_reset_date = now
                analytics.save()

                # ── Wipe raw view tracking for this company ──────────────────
                # PropertyViews and SessionId are raw event records.
                # The rolling averages above are the permanent summary we keep.
                # Wiping them here is safe — the data has already been
                # rolled into the averages.
                uid = company.unique_company_id
                deleted_views, _   = PropertyViews.objects.filter(uuid=uid).delete()
                deleted_sessions, _ = SessionId.objects.filter(company_uuid=uid).delete()

                reset_count += 1

                self.stdout.write(
                    f'  Reset: {company.company_name} — '
                    f'{deleted_views} views wiped, '
                    f'{deleted_sessions} sessions wiped.'
                )

            else:
                # Not due yet — show how many days remain so you can
                # verify in logs that the gate is working correctly
                days_remaining = 30 - time_difference.days
                skip_count += 1

                self.stdout.write(
                    f'  Skip:  {company.company_name} — '
                    f'{days_remaining} day(s) until next reset.'
                )

        # ── Summary ──────────────────────────────────────────────────────────
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone at {now.strftime("%Y-%m-%d %H:%M:%S")} UTC — '
                f'{reset_count} reset, {skip_count} skipped.'
            )
        )