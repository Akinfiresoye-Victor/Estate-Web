# ─────────────────────────────────────────────────────────────────────────────
# management/commands/reset_analytics.py
#
# Resets 30-day analytics counters for ALL companies and ALL agents
# whose 30-day window has expired.
#
# Run manually:
#   python manage.py reset_analytics
#
# Force reset everything immediately (for testing):
#   python manage.py reset_analytics --force
#
# Schedule on Render (separate from refresh_scores):
#   0 2 * * *  python manage.py reset_analytics
#   0 3 * * *  python manage.py refresh_scores
# ─────────────────────────────────────────────────────────────────────────────

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from companies.models import CompanyAnalytics
from companies.models import SessionId as company_session
from agents.models  import AgentAnalytics
from agents.models import SessionId as agent_session
from core.models   import PropertyViews


class Command(BaseCommand):
    help = 'Resets 30-day analytics counters for companies and agents whose window has expired.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset all companies and agents immediately, ignoring the 30-day gate.',
        )
        parser.add_argument(
            '--companies-only',
            action='store_true',
            help='Only reset company analytics, skip agents.',
        )
        parser.add_argument(
            '--agents-only',
            action='store_true',
            help='Only reset agent analytics, skip companies.',
        )

    def handle(self, *args, **options):
        force          = options['force']
        companies_only = options['companies_only']
        agents_only    = options['agents_only']
        now            = timezone.now()

        self.stdout.write(
            f'\nStarting analytics reset at {now.strftime("%Y-%m-%d %H:%M:%S")} UTC\n'
            f'{"(FORCE MODE — ignoring 30-day gate)" if force else ""}'
        )

        if not agents_only:
            self._reset_companies(now, force)

        if not companies_only:
            self._reset_agents(now, force)

        self.stdout.write(self.style.SUCCESS('\nAll done.'))

    # ── Company reset ─────────────────────────────────────────────────────────

    def _reset_companies(self, now, force):
        self.stdout.write('\n── Companies ──────────────────────────────')

        all_analytics = CompanyAnalytics.objects.select_related('company').all()
        reset_count   = 0
        skip_count    = 0

        for analytics in all_analytics:
            company         = analytics.company
            time_difference = now - analytics.last_reset_date

            if force or time_difference >= timedelta(days=30):

                # Rolling averages — bake this month into the running average
                # before wiping the counters
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

                # Wipe current month counters
                analytics.profile_views    = 0
                analytics.property_views_l = 0
                analytics.property_views_s = 0
                analytics.monthly_leads    = 0
                analytics.monthly_reviews  = 0

                # Move the window forward — views now filter from this point
                analytics.last_reset_date = now
                analytics.save()

                # Wipe raw tracking records — averages above are the
                # permanent record, these are just raw event logs
                uid                  = company.unique_company_id
                deleted_views, _     = PropertyViews.objects.filter(uuid=uid).delete()
                deleted_sessions, _  = company_session.objects.filter(company=company).delete()

                reset_count += 1
                self.stdout.write(
                    f'  Reset: {company.company_name} — '
                    f'{deleted_views} views, {deleted_sessions} sessions wiped.'
                )

            else:
                days_remaining = 30 - time_difference.days
                skip_count    += 1
                self.stdout.write(
                    f'  Skip:  {company.company_name} — '
                    f'{days_remaining} day(s) remaining.'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'  Companies: {reset_count} reset, {skip_count} skipped.'
            )
        )

    # ── Agent reset ───────────────────────────────────────────────────────────

    def _reset_agents(self, now, force):
        self.stdout.write('\n── Agents ─────────────────────────────────')

        all_analytics = AgentAnalytics.objects.select_related('agent').all()
        reset_count   = 0
        skip_count    = 0

        for analytics in all_analytics:
            agent           = analytics.agent
            time_difference = now - analytics.last_reset_date

            if force or time_difference >= timedelta(days=30):

                # Rolling averages
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

                # Wipe current month counters
                analytics.profile_views    = 0
                analytics.property_views_l = 0
                analytics.property_views_s = 0
                analytics.monthly_leads    = 0
                analytics.monthly_reviews  = 0

                # Move the window forward
                analytics.last_reset_date = now
                analytics.save()

                # Wipe raw tracking records for this agent
                # SessionId uses agent FK directly, not a uuid string
                deleted_views, _    = PropertyViews.objects.filter(
                    uuid=agent.agent_uuid
                ).delete()
                deleted_sessions, _ = agent_session.objects.filter(
                    agent=agent
                ).delete()

                reset_count += 1
                self.stdout.write(
                    f'  Reset: {agent.first_name} {agent.last_name} — '
                    f'{deleted_views} views, {deleted_sessions} sessions wiped.'
                )

            else:
                days_remaining = 30 - time_difference.days
                skip_count    += 1
                self.stdout.write(
                    f'  Skip:  {agent.first_name} {agent.last_name} — '
                    f'{days_remaining} day(s) remaining.'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'  Agents: {reset_count} reset, {skip_count} skipped.'
            )
        )