from django.shortcuts import render, redirect
from .forms import SocialLinksFormset, CompanyForm,JobPostForm, InviteLinkForm, EditEmployeeForm
from django.template.loader import render_to_string
from core.utils import send_estate_email
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import *
from core.models import PropertyManagementRent, PropertyManagementSale, PropertyViews, Appointments, ErrorLog
from estate.models import LeadInfo
from members.models import User
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, timedelta
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Sum
from core.utils import *
from agents.models import AgentInformation
from django.urls import reverse
import threading
import traceback
from django_ratelimit.decorators import ratelimit



def calculate_profile_strength(has_logo, has_agent, is_verified):
    """
    Lives outside the view — defined once, not recreated on every request.
    """
    score = 0
    if has_logo:    score += 20
    if has_agent:   score += 30
    if is_verified: score += 50
    return score


def dashboard(request):
    """
    HomePage for companies
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to access page')
        return redirect('landing')

    if request.user.role != 'company':
        messages.error(request, 'Company account only')
        return redirect('landing')

    try:
        company= CompanyInformation.objects.get(user_id=request.user.id)
        social_links = company.social.all()
        if company.user_id != request.user.id:
            messages.error(request, 'Error Redirecting To Dashboard....')
            return redirect('landing')
        analytics, _ = CompanyAnalytics.objects.get_or_create(
            company=company,
            defaults={
                'profile_views':         0,
                'property_views_l':      0,
                'property_views_s':      0,
                'average_profile_views': 0,
                'average_lease_views':   0,
                'average_sale_views':    0,
                'monthly_leads':         0,
                'monthly_reviews':       0,
                'average_leads':         0,
                'average_reviews':       0,
            }
        )

        #shwing data based on the last 30 days
        window_start = analytics.last_reset_date

        #Properties ID 
        rent_ids = set(PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id).values_list('pk', flat=True))
        sale_ids = set(PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id).values_list('pk', flat=True))

        # ── Property views based on the last 30 days
        lease_views = PropertyViews.objects.filter(property_type='Rent',property_id__in=rent_ids).count()
        sale_views = PropertyViews.objects.filter(property_type='Sale',property_id__in=sale_ids).count()

        # ── Likes
        rent_likes = PropertyManagementRent.objects.filter(pk__in=rent_ids).aggregate(total=Sum('total_likes'))['total'] or 0

        sale_likes = PropertyManagementSale.objects.filter(pk__in=sale_ids).aggregate(total=Sum('total_likes'))['total'] or 0

        total_liked_prop = rent_likes + sale_likes

        # ── Counts
        total_prop     = len(rent_ids) + len(sale_ids)  # free — sets already in memory
        employee_count = Employees.objects.filter(company=company).count()

        # Inquiries filtered to current 30-day window
        total_inq = LeadInfo.objects.filter(
            company_uuid=company.unique_company_id,
            date_created__gte=window_start
        ).count()

        # All-time rating — users expect to see full history, not just this month
        rating_data = CompanyRating.objects.filter(
            company_uuid=company.unique_company_id
        ).aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))

        average_rating = rating_data['avg_rating'] or 0.0
        total_reviews  = rating_data['total_reviews']
        rating_score   = average_rating * total_reviews

        analytics.property_views_l = lease_views
        analytics.property_views_s = sale_views

        avg_property_view = analytics.average_lease_views + analytics.average_sale_views
        #Calculating ranking based on specific analytics
        eng_rate              = engagement_rate(
            total_liked_prop,
            avg_property_view,
            analytics.average_profile_views,
            rating_score
        )
        analytics.competition = eng_rate
        analytics.save()

        # Getting other companies scores to make ranking efficient
        all_analytics = CompanyAnalytics.objects.select_related('company').all()

        #calculating saved properties count of each and every company:The company UUID is the key and the total is the value
        rent_likes_by_company = {
            item['company_uuid']: item['total']
            for item in PropertyManagementRent.objects.values('company_uuid')
            .annotate(total=Sum('total_likes'))
        }
        sale_likes_by_company = {
            item['company_uuid']: item['total']
            for item in PropertyManagementSale.objects.values('company_uuid')
            .annotate(total=Sum('total_likes'))
        }
        ratings_by_company = {
            item['company_uuid']: {
                'avg':   item['avg_rating'] or 0.0,
                'count': item['total_reviews']
            }
            for item in CompanyRating.objects.values('company_uuid')
            .annotate(avg_rating=Avg('rating'), total_reviews=Count('id'))
        }

        #final calculation of all companies analytics
        total_eng = []
        for comp_analytics in all_analytics:
            uid = comp_analytics.company.unique_company_id

            comp_total_likes = ((rent_likes_by_company.get(uid) or 0) +(sale_likes_by_company.get(uid) or 0))
            comp_rating       = ratings_by_company.get(uid, {'avg': 0.0, 'count': 0})
            comp_rating_score = comp_rating['avg'] * comp_rating['count']
            comp_avg_prop_views = (comp_analytics.average_sale_views +comp_analytics.average_lease_views)
            comp_eng_rate = engagement_rate(
                comp_total_likes,
                comp_avg_prop_views,
                comp_analytics.average_profile_views,
                comp_rating_score
            )
            total_eng.append(comp_eng_rate)

        # ── Market position
        total_eng_sum         = sum(total_eng)
        calculated_engagement = total_companies_engagement_calculator(
            total_eng_sum,
            analytics.competition,
            company.unique_company_id,
            avg_property_view
        )

        #ordering them based on their engagement scores
        if total_eng and len(total_eng) > 1:
            sorted_eng      = sorted(total_eng, reverse=True)
            companies_above = sum(1 for eng in sorted_eng if eng > analytics.competition)
            market_position = (companies_above / len(sorted_eng)) * 100

            if market_position <= 1:
                top_performer = "Top 1%"
            elif market_position <= 5:
                top_performer = "Top 5%"
            elif market_position <= 10:
                top_performer = "Top 10%"
            elif market_position <= 25:
                top_performer = "Top 25%"
            elif market_position <= 50:
                top_performer = "Top 50%"
            else:
                top_performer = f"Top {int(market_position)}%"
        else:
            top_performer   = "New Listing"
            market_position = 100

        #  Profile strength
        has_logo    = bool(company.company_logo)
        has_agent   = employee_count > 0
        is_verified = company.verified

        # ── Recent activity — filtered to current 30-day window
        recent_activities = CompanyActivityLog.objects.filter(
            company=company,
            timestamp__gte=window_start
        ).order_by('-timestamp')[:5]

        context = {
            'company':          company,
            'social_links':     social_links,
            'total_properties': total_prop,
            'total_views':      analytics.profile_views,
            'total_inquiries':  total_inq,
            'average_rating':   average_rating,
            'total_reviews':    total_reviews,
            'competition':      top_performer,
            'market_position':  round(market_position, 1),
            'engagement_rate':  analytics.competition,
            'is_company_admin': request.user.id == company.user_id,
            'has_logo':         has_logo,
            'has_agent':        has_agent,
            'is_kyc_verified':  is_verified,
            'profile_strength': calculate_profile_strength(has_logo, has_agent, is_verified),
            'recent_activities': recent_activities,
            'window_start':     window_start,  # show "Since [date]" in template
        }
        return render(request, 'company/dashboard.html', context)

    except CompanyInformation.DoesNotExist:
        messages.warning(request, 'Please set up your company profile to continue.')
        return redirect('company:company_form')

    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


#form all companies must fill before they access the dashboard
def company_form(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.error(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    try:
        submitted=False
        if request.method == 'POST':
            try:
                CompanyInformation.objects.get(user_id=request.user.id)
                return redirect('company:dashboard')
            except CompanyInformation.DoesNotExist:
                comp_form=CompanyForm(request.POST or None, request.FILES or None)
                link_form=SocialLinksFormset(request.POST or None)
                with transaction.atomic():
                    if comp_form.is_valid() and link_form.is_valid():
                        company_form=comp_form.save(commit=False)
                        company_form.user_id= request.user.id
                        User.email= company_form.email
                        company_form.save()
                        link_form.instance=company_form
                        link_form.save()
                        messages.success(request, 'Company profile successfully created.')
                        return HttpResponseRedirect('?submitted=True')
                CompanyActivityLog.objects.create(
                company=CompanyInformation.objects.get(user_id=request.user.id),
                action='Joined Estate Web'
        )
        else:
            comp_form= CompanyForm()
            link_form= SocialLinksFormset()
            if 'submitted' in request.GET:
                submitted=True
        return render(request, 'company/company_form.html', {
                                                            'form': comp_form,
                                                            'social': link_form,
                                                            'submitted': submitted
                    })
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def update_company_profile(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.info(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    try:
        company_information=CompanyInformation.objects.get(user_id=request.user.id)
        if request.user.id != company_information.user_id:
            messages.error(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        if request.method == 'POST':
            comp_form = CompanyForm(request.POST, request.FILES, instance=company_information)
            link_form = SocialLinksFormset(request.POST, request.FILES, instance=company_information)
            if comp_form.is_valid() and link_form.is_valid():
                with transaction.atomic():
                    company = comp_form.save(commit=False)
                    company.user_id = request.user.id
                    company.save()
                    link_form.save()
                    messages.success(request, 'Company profile updated successfully.')
                    return redirect('company:company-settings')
        else:
            comp_form = CompanyForm(instance=company_information)
            link_form = SocialLinksFormset(instance=company_information)
            CompanyActivityLog.objects.create(
                company=company_information,
                action='Company Details Updated'
            )
        return render(request, 'company/update_company_profile.html', {
            'form':comp_form,
            'social': link_form
        })
    except ObjectDoesNotExist:
        messages.info(request, 'Company profile data is missing.')
        return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def company_analytics(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Login required')
        return redirect('login')

    if request.user.role != 'company':
        messages.error(request, 'Company account only')
        return redirect('landing')

    try:
        messages.info(request, 'Numbers might seem low since we just launched')

        company = CompanyInformation.objects.get(user_id=request.user.id)
        if company.user_id != request.user.id:
            messages.error(request, 'Unauthorized access')
            return redirect('landing')
        analytics, _ = CompanyAnalytics.objects.get_or_create(
            company=company,
            defaults={
                'profile_views':         0,
                'property_views_l':      0,
                'property_views_s':      0,
                'average_profile_views': 0,
                'average_lease_views':   0,
                'average_sale_views':    0,
                'monthly_leads':         0,
                'monthly_reviews':       0,
                'average_leads':         0,
                'average_reviews':       0,
            }
        )

        #30 days window for company analytics
        window_start = analytics.last_reset_date

        # ── Property IDs — fetched once, reused below
        rent_ids = set(PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id).values_list('pk', flat=True))
        sale_ids = set(PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id).values_list('pk', flat=True))

        # ── Property views
        # PropertyViews is wiped by the cron on reset so no date filter needed.
        # Everything in the table already belongs to the current window.
        lease_views = PropertyViews.objects.filter(
            property_type='Rent',
            property_id__in=rent_ids
        ).count()

        sale_views = PropertyViews.objects.filter(
            property_type='Sale',
            property_id__in=sale_ids
        ).count()

        # ── Leads — filtered to current 30-day window ────────────────────────
        monthly_leads = LeadInfo.objects.filter(
            company_uuid=company.unique_company_id,
            date_created__gte=window_start
        ).count()

        # ── Ratings ──────────────────────────────────────────────────────────
        # All-time rating shown for display — users expect full rating history.
        # monthly_reviews is a separate counter just for the monthly trend stat.
        all_time_rating = CompanyRating.objects.filter(
            company_uuid=company.unique_company_id
        ).aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))

        monthly_reviews = CompanyRating.objects.filter(
            company_uuid=company.unique_company_id,
            created_at__gte=window_start
        ).count()

        average_rating = all_time_rating['avg_rating'] or 0.0
        total_reviews  = all_time_rating['total_reviews']
        rating_score   = average_rating * total_reviews

        # ── Likes ────────────────────────────────────────────────────────────
        rent_likes = PropertyManagementRent.objects.filter(
            pk__in=rent_ids
        ).aggregate(total=Sum('total_likes'))['total'] or 0

        sale_likes = PropertyManagementSale.objects.filter(
            pk__in=sale_ids
        ).aggregate(total=Sum('total_likes'))['total'] or 0

        total_liked_prop = rent_likes + sale_likes

        # ── Update analytics — no reset logic here ───────────────────────────
        # reset_button() has been removed entirely. The cron job handles resets.
        # This view only updates running counters and saves once.
        analytics.property_views_l = lease_views
        analytics.property_views_s = sale_views
        analytics.monthly_leads    = monthly_leads
        analytics.monthly_reviews  = monthly_reviews

        avg_prop_views = analytics.average_lease_views + analytics.average_sale_views

        eng_rate              = engagement_rate(
            total_liked_prop,
            avg_prop_views,
            analytics.average_profile_views,
            rating_score
        )
        analytics.competition = eng_rate
        analytics.save()

        # ── Percentage changes vs last month's rolling average ───────────────
        # monthly_change() compares this month's count against the stored
        # rolling average to produce a +/- percentage for the template.
        lease_views_change   = monthly_change(analytics.property_views_l, analytics.average_lease_views)
        sale_views_change    = monthly_change(analytics.property_views_s, analytics.average_sale_views)
        profile_views_change = monthly_change(analytics.profile_views, analytics.average_profile_views)
        leads_change         = monthly_change(monthly_leads, analytics.average_leads)
        reviews_change       = monthly_change(monthly_reviews, analytics.average_reviews)
        total_prop_incr_perc = (sale_views_change + lease_views_change) / 2

        # ── Competition loop — bulk queries, zero per-company DB hits ────────
        all_analytics = CompanyAnalytics.objects.select_related('company').all()

        rent_likes_by_company = {
            item['company_uuid']: item['total']
            for item in PropertyManagementRent.objects.values('company_uuid')
            .annotate(total=Sum('total_likes'))
        }
        sale_likes_by_company = {
            item['company_uuid']: item['total']
            for item in PropertyManagementSale.objects.values('company_uuid')
            .annotate(total=Sum('total_likes'))
        }
        ratings_by_company = {
            item['company_uuid']: {
                'avg':   item['avg_rating'] or 0.0,
                'count': item['total_reviews']
            }
            for item in CompanyRating.objects.values('company_uuid')
            .annotate(avg_rating=Avg('rating'), total_reviews=Count('id'))
        }

        total_companies_eng = []

        for comp_analytics in all_analytics:
            uid = comp_analytics.company.unique_company_id

            comp_total_likes = (
                (rent_likes_by_company.get(uid) or 0) +
                (sale_likes_by_company.get(uid) or 0)
            )
            comp_rating       = ratings_by_company.get(uid, {'avg': 0.0, 'count': 0})
            comp_rating_score = comp_rating['avg'] * comp_rating['count']
            comp_avg_prop_views = (
                comp_analytics.average_sale_views +
                comp_analytics.average_lease_views
            )
            comp_eng_rate = engagement_rate(
                comp_total_likes,
                comp_avg_prop_views,
                comp_analytics.average_profile_views,
                comp_rating_score
            )
            total_companies_eng.append(comp_eng_rate)

        # ── Market position ──────────────────────────────────────────────────
        total_eng_sum         = sum(total_companies_eng)
        calculated_engagement = total_companies_engagement_calculator(
            total_eng_sum,
            analytics.competition,
            company.unique_company_id,
            avg_prop_views
        )

        if total_companies_eng and len(total_companies_eng) > 1:
            sorted_eng      = sorted(total_companies_eng, reverse=True)
            companies_above = sum(1 for eng in sorted_eng if eng > analytics.competition)
            market_position = (companies_above / len(sorted_eng)) * 100

            if market_position <= 1:
                top_performer = "Top 1%"
            elif market_position <= 5:
                top_performer = "Top 5%"
            elif market_position <= 10:
                top_performer = "Top 10%"
            elif market_position <= 25:
                top_performer = "Top 25%"
            else:
                top_performer = f"Top {int(market_position)}%"
        else:
            top_performer   = "New Listing"
            market_position = 100

        competition_pct = calculated_engagement[0]
        inq_conv_rate   = calculated_engagement[1]

        # ── Top 4 properties — two queries instead of one per property ───────
        prop_rent      = list(PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id))
        prop_sale      = list(PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id))
        all_properties = prop_rent + prop_sale
        all_properties.sort(key=lambda x: x.total_likes, reverse=True)
        top_properties = all_properties[:4]

        top_rent_ids = [p.pk for p in top_properties if p in prop_rent]
        top_sale_ids = [p.pk for p in top_properties if p in prop_sale]

        rent_view_counts = {
            item['property_id']: item['cnt']
            for item in PropertyViews.objects.filter(
                property_type='Rent',
                property_id__in=top_rent_ids
            ).values('property_id').annotate(cnt=Count('id'))
        }
        sale_view_counts = {
            item['property_id']: item['cnt']
            for item in PropertyViews.objects.filter(
                property_type='Sale',
                property_id__in=top_sale_ids
            ).values('property_id').annotate(cnt=Count('id'))
        }

        view_list = []
        for prop in top_properties:
            if prop in prop_rent:
                view_list.append(rent_view_counts.get(prop.pk, 0))
            else:
                view_list.append(sale_view_counts.get(prop.pk, 0))

        likes_views = zip(top_properties, view_list)

        # ── Recent activity — filtered to current 30-day window ─────────────
        recent_activities = CompanyActivityLog.objects.filter(
            company=company,
            timestamp__gte=window_start
        ).order_by('-timestamp')[:10]

        return render(request, 'company/company_analytics.html', {
            'profile_views':         analytics.profile_views,
            'prop_views':            analytics.property_views_l + analytics.property_views_s,
            'leased_view':           analytics.property_views_l,
            'sale_view':             analytics.property_views_s,
            'profile_incr_perc':     profile_views_change,
            'lease_incr_perc':       lease_views_change,
            'sale_incr_perc':        sale_views_change,
            'total_prop_incr_perc':  total_prop_incr_perc,
            'monthly_leads':         monthly_leads,
            'leads_change':          leads_change,
            'monthly_reviews':       monthly_reviews,
            'reviews_change':        reviews_change,
            'average_rating':        average_rating,
            'total_reviews':         total_reviews,
            'engagement_rate':       analytics.competition,
            'competition':           top_performer,
            'market_position':       round(market_position, 1),
            'inq_rate':              inq_conv_rate,
            'ranking':               likes_views,
            'recent_activities':     recent_activities,
            'window_start':          window_start,  # use in template as "Since {{ window_start|date:'M d' }}"
        })

    except CompanyInformation.DoesNotExist:
        messages.error(request, "Company profile not found.")
        return redirect('landing')

    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
def documents(request):
    return render(request, 'company/documents.html', {})

def reports(request):
    pass

def company_settings(request):
    
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'company':
        messages.error(request, 'Companies Only')
        return redirect('landing')
    
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)
        if company.user_id != request.user.id:
            messages.error(request, 'Something happned on our end')
            return redirect('landing')
        context={
            'company':company,
        }
        return render(request, 'company/company_settings.html', context)
    except ObjectDoesNotExist:
        messages.error(request, 'Error Company Info Missing')
        return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def lead_management(request):
    try:
        if not request.user.is_authenticated:
            messages.info(request, 'Login required')
            return redirect('login')
        if request.user.role != 'company':
            messages.error(request, 'Company account only')
            return redirect('landing')
        company_uuid=CompanyInformation.objects.filter(user_id=request.user.id).values_list('unique_company_id', flat=True).first()
        general_leads=LeadInfo.objects.filter(company_uuid=company_uuid)
        p=Paginator(general_leads.order_by('-date_created'), 10)
        page=request.GET.get('page')
        leads=p.get_page(page)
        nums="a" * leads.paginator.num_pages
        lead_count=general_leads.count()
        new_leads=general_leads.filter(date_created=date.today()).count()
        
        
        '''Lead Stages'''
        potential_friend=general_leads.filter(stages='Potential Friend')
        true_friend=general_leads.filter(stages='True Friend')
        contracted=general_leads.filter(stages='Contracted')
        closed=general_leads.filter(stages='Closed/Won')
        disposition=general_leads.filter(stages='Disposition')
        new_lead_stage=general_leads.filter(stages='New')
        
        '''Lead Status'''
        contacted=general_leads.filter(status='Contacted')
        not_contacted=general_leads.filter(status= 'Not Contacted')
        attempt_contact=general_leads.filter(status= 'Contact Attempt')
        cold_lead= general_leads.filter(status= 'Cold Lead')
        warm_lead=general_leads.filter(status= 'Warm Lead')
        hot_lead=general_leads.filter(status= 'Hot Lead')
        qualified=general_leads.filter(status= 'Qualified')
        unqualified=general_leads.filter(status= 'Unqualified')


        context= {'lead_count':lead_count, 'new_leads': new_leads, 'leads':leads,'potential':potential_friend,
                    'potential_count': potential_friend.count(),'true_friend': true_friend,'true_friend_count':true_friend.count(),
                    'contracted':contracted,'contracted_count':contracted.count(),'closed':closed,'closed_count':closed.count(),
                    'disposition': disposition, 'disposition_count':disposition.count(), 'contacted':contacted, 'not_contacted':not_contacted,
                    'attempt':attempt_contact, 'cold_lead':cold_lead, 'warm_lead':warm_lead, 'hot_lead':hot_lead,
                    'qulified':qualified, 'unqualified':unqualified, 'nums': nums, 'new_stage':new_lead_stage.count()}
        return render(request, 'company/lead_management.html', context)
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def lead_detail(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.info(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)
        client=LeadInfo.objects.get(lead_id=lead_id)
        if client.company_uuid != company.unique_company_id:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        try:
            if client.property_type =='Sale':
                property=PropertyManagementSale.objects.get(pk=client.property_intrested)
            elif client.property_type == 'Rent':
                property=PropertyManagementRent.objects.get(pk=client.property_intrested)
        except ObjectDoesNotExist:
            property=None
        return render(request, 'company/lead_detail_page.html', {'lead':client, 'property':property})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def delete_lead(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.error(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        company= CompanyInformation.objects.get(user_id=request.user.id)
        lead_to_delete=LeadInfo.objects.get(lead_id=lead_id)
        if company.unique_company_id != lead_to_delete.company_uuid:
            messages.error(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        if lead_to_delete.schedule_tour:
            appointment=Appointments.objects.filter(lead_uuid=lead_to_delete.lead_id)
            appointment.delete()
        lead_to_delete.delete()
        messages.success(request, "Lead deleted successfully.")
        CompanyActivityLog.objects.create(
            company=company,
            action='Lead Deleted'
        )
        return redirect('company:lead-management')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



@require_POST
def update_lead_status(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('landing')
    if request.user.role !='company':
        messages.info(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        try:
            company= CompanyInformation.objects.get(user_id= request.user.id)
            lead=LeadInfo.objects.get(pk=lead_id)
            if lead.company_uuid != company.unique_company_id:
                messages.error(request, 'Access denied: Unauthorized action.')
                return redirect('landing')
            new_status= request.POST.get('new_status')
            if not new_status:
                messages.error(request, 'Please provide a lead status.')
                return redirect('company:lead-management')
            
            from core.choices import LEAD_STATUS
            if new_status not in [choice[0] for choice in LEAD_STATUS]:
                messages.error(request, 'The provided status value is invalid.')
                return redirect('company:lead-management')
            
            lead.status=new_status
            lead.date_updated=timezone.now()
            lead.save()
            CompanyActivityLog.objects.create(
                company=company,
                action='Lead Status Updated'
            )
            messages.success(request, 'Lead status updated successfully.')
            return redirect('company:lead-detail', lead_id=lead_id)
        except ObjectDoesNotExist:
            messages.error(request, 'The requested lead could not be found.')
            return redirect('company:lead-management')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



@require_POST
def update_lead_stage(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('landing')
    if request.user.role != 'company':
        messages.info(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        try:
            company= CompanyInformation.objects.get(user_id= request.user.id)
            lead=LeadInfo.objects.get(pk=lead_id)
            if lead.company_uuid != company.unique_company_id:
                messages.error(request, 'Access denied: Unauthorized action.')
                return redirect('landing')
            new_stage = request.POST.get('new_stage')
            if not new_stage:
                messages.error(request, 'Please provide a lead stage.')
                return redirect('company:lead-management')
            
            from core.choices import LEAD_STAGES
            if new_stage not in [choice[0] for choice in LEAD_STAGES]:
                messages.error(request, 'The provided stage value is invalid.')
                return redirect('company:lead-management')
            
            lead.stages = new_stage
            lead.date_updated=timezone.now()
            lead.save()
            CompanyActivityLog.objects.create(
                company=company,
                action= 'Lead Stage Updated'
            )
            messages.success(request, 'Lead stage updated successfully.')
            return redirect('company:lead-detail', lead_id=lead_id)
        except ObjectDoesNotExist:
            messages.error(request, 'The requested lead could not be found.')
            return redirect('company:lead-management')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def properties_by_company(request, company_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role !='customer':
        messages.info(request, 'Access denied: This page is for customer accounts only.')
        return redirect('landing')
    try:
        company=CompanyInformation.objects.filter(unique_company_id=company_uuid).values_list('user_id', flat=True).first()
        on_lease=PropertyManagementRent.objects.filter(company_uuid=company_uuid)
        on_sale=PropertyManagementSale.objects.filter(company_uuid=company_uuid)
        return render(request, 'company/company_properties.html', {
            'on_lease': on_lease,
            'on_sale': on_sale,
            'company':company
        })
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def find_talents(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('landing')
    if request.user.role !='company':
        messages.info(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        agents = AgentInformation.objects.all()
        return render(request, 'company/find_talents.html',{'agents':agents})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def manage_applications(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('landing')
    if request.user.role != 'company':
        messages.info(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        company = CompanyInformation.objects.get(user_id=request.user.id)
        company_job_posts = JobPost.objects.filter(company_uuid=company.unique_company_id)
        
        today = timezone.now().date()
        jobs_data = [
            (job, (today - job.date_posted).days)
            for job in company_job_posts
        ]
        
        total_applicants = sum(job.applicants for job in company_job_posts)
        
        context = {
            'job_count': company_job_posts.count(),
            'jobs': jobs_data,
            'total_applicants': total_applicants
        }
        return render(request, 'company/manage_applications.html', context)
    except CompanyInformation.DoesNotExist:
        messages.error(request, 'Company profile data is missing.')
        return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def manage_company(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('landing')
    if request.user.role !='company':
        messages.info(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)

        # Run expiry check only on currently active links
        active_links=InviteLink.objects.filter(company=company, is_active=True)
        for link in active_links:
            if timezone.now() >= link.expires_at:
                link.is_active=False
            if link.max_uses is not None and link.use_count >= link.max_uses:
                link.is_active=False
            link.save()

        # Delete inactive links that expired more than 24 hours ago
        InviteLink.objects.filter(
            company=company,
            expires_at__lt=timezone.now() - timedelta(hours=24)
        ).delete()

        # Fetch ALL links (active + revoked) for displa y in the panel
        invite_links=InviteLink.objects.filter(company=company).order_by('-created_at')
        employees=Employees.objects.filter(company=company)
        employee_count=employees.count()
        department_count=employees.values('company_department').distinct().count()
        activitylog=CompanyActivityLog.objects.filter(company=company).order_by('-timestamp')[:10]
        return render(request, 'company/manage_company.html', {
            'employees': employees,
            'total_employees': employee_count,
            'active_agents': employee_count,  # adjust if you add a status field later
            'departments_count': department_count,
            'invite_links': invite_links,
            'active_invite_links_count': invite_links.filter(is_active=True).count(),
            'activity_logs':activitylog ,
            'form': InviteLinkForm(),
            'invite_url': None,  # None by default, set to the URL string after generation
        })
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def delete_company(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.info(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        company_data= CompanyInformation.objects.get(user_id=request.user.id)
        if company_data.user_id != request.user.id:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        leads= LeadInfo.objects.filter(company_uuid=company_data.unique_company_id)
        appointments=Appointments.objects.filter(company_uuid=company_data.unique_company_id)
        property_views=PropertyViews.objects.filter(uuid=company_data.unique_company_id)
        properties_on_rent=PropertyManagementRent.objects.filter(company_uuid=company_data.unique_company_id)
        properties_on_sale=PropertyManagementSale.objects.filter(company_uuid=company_data.unique_company_id)
        user_id=User.objects.get(pk=request.user.id)
        ratings=CompanyRating.objects.filter(company_uuid=company_data.unique_company_id)
        try:
            leads.delete()
            appointments.delete()
            property_views.delete()
            properties_on_rent.delete()
            properties_on_sale.delete()
            ratings.delete()
            user_id.delete()
        except:
            messages.error(request, 'An unexpected error occurred. Please try again.')
            return redirect('landing')
        messages.success(request, 'Company account and all associated data deleted successfully.')
        return redirect('landing')
    except ObjectDoesNotExist:
        user_id=User.objects.get(pk=request.user.id)
        user_id.delete()
        messages.error(request, 'The company profile could not be found User Data Deleted.')
        return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def vacancy_form(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    
    if request.user.role != 'company':
        messages.warning(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        company = CompanyInformation.objects.get(user_id=request.user.id)
        
        if request.method == 'POST':
            job_form = JobPostForm(request.POST or None, request.FILES or None)
            
            if job_form.is_valid():
                with transaction.atomic():
                    job = job_form.save(commit=False)
                    job.user_id = request.user.id
                    job.company_uuid = company.unique_company_id
                    job.company=company
                    job.company_name=company.company_name
                    job.save()
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Job Posted'
                    )
                    messages.success(request, 'Job listing posted successfully.')
                    return redirect('company:application-management')
            else:
                # Display form errors
                for field, errors in job_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            job_form = JobPostForm()
        
        context = {
            'form': job_form,
            'company': company
        }
        return render(request, 'company/vacancy_form.html', context)
        
    except ObjectDoesNotExist:
        messages.error(request, 'Company profile not found. Please complete your profile before posting a job.')
        return redirect('landing')
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def update_vacancy(request, job_id):
    """View to update an existing job posting"""
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    
    if request.user.role != 'company':
        messages.warning(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    company=CompanyInformation.objects.get(user_id= request.user.id)
    job = JobPost.objects.get(pk=job_id, user_id=request.user.id)
    if job.company_uuid != company.unique_company_id:
        messages.error(request, 'Access denied: You do not have permission to edit this job listing.')
        return redirect('landing')
    try:
        if request.method == 'POST':
            job_form = JobPostForm(request.POST, request.FILES, instance=job)
            
            if job_form.is_valid():
                with transaction.atomic():
                    job_form.save()
                    messages.success(request, 'Job listing updated successfully.')
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Job Post Updated'
                    )
                    return redirect('company:application-management')
            else:
                for field, errors in job_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            job_form = JobPostForm(instance=job)
        
        context = {
            'form': job_form,
            'job': job,
            'is_update': True
        }
        return render(request, 'company/vacancy_form.html', context)
        
    except JobPost.DoesNotExist:
        messages.error(request, 'Job listing not found or unauthorized access.')
        return redirect('company:application-management')
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def delete_vacancy(request, job_id):
    """View to delete a job posting"""
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    
    if request.user.role != 'company':
        messages.warning(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        job = JobPost.objects.get(pk=job_id, user_id=request.user.id)
        company=CompanyInformation.objects.get(user_id=request.user.id)
        if job.company_uuid != company.unique_company_id:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        job_title = job.job_title
        job.delete()
        CompanyActivityLog.objects.create(
        company=company,
        action= 'Job Post Deleted'
        )
        messages.success(request, f'Job listing "{job_title}" has been deleted successfully.')
        return redirect('company:application-management')
        
    except JobPost.DoesNotExist:
        messages.error(request, 'Job listing not found or unauthorized access.')
        return redirect('company:application-management')
        
    except Exception:
        messages.error(request, 'An unexpected error occurred while deleting the job listing.')
        return redirect('company:application-management')

@ratelimit(key='ip', rate='30/m', method='POST', block=True)
def toggle_job_status(request, job_id):
    """Toggle job active/inactive status"""
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    
    if request.user.role != 'company':
        messages.warning(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        job = JobPost.objects.get(pk=job_id, user_id=request.user.id)
        company=CompanyInformation.objects.get(user_id=request.user.id)
        if job.company_uuid != company.unique_company_id:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        job.is_active = not job.is_active
        job.save()
        CompanyActivityLog.objects.create(
            company=company,
            action= 'Job Post Updated'
        )
        
        status = "activated" if job.is_active else "deactivated"
        messages.success(request, f'The job listing "{job.job_title}" has been {status} successfully.')
        return redirect('company:application-management')
        
    except JobPost.DoesNotExist:
        messages.error(request, 'The requested job listing could not be found.')
        return redirect('company:application-management')
        
    except Exception:
        messages.error(request, 'An unexpected error occurred.')
        return redirect('company:application-management')



#for manual add
def onboard_agent(request, agent_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.info(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        agent=AgentInformation.objects.get(agent_uuid=agent_uuid)
        company=CompanyInformation.objects.get(user_id=request.user.id)
        if company.user_id != request.user.id:
            messages.error(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        try:
            #checking if employee is present
            Employees.objects.get(agent_uuid=agent_uuid)
            messages.success(request, 'Agent has been added successfully.')
            return redirect('landing')
        except ObjectDoesNotExist:
            Employees.objects.create(
                company=company,
                agent_name=f'{agent.first_name} {agent.first_name}',
                company_department='Unassigned',
                company_role=agent.work_type,
                agent_email=agent.email,
                agent_phone_no=agent.phone_number,
                agent_uuid=agent.agent_uuid,
                agent_headshot=agent.profile_picture,
            )
            agent.company_uuid=company.unique_company_id
            agent.save()

            # Send email to agent (background thread)
            threading.Thread(
                target=send_estate_email,
                kwargs=dict(
                    subject=f"You've joined {company.company_name}!",
                    template_name='emails/agent_joined_notification.html',
                    context={'agent': agent.users, 'company': company, 'request': request},
                    recipient_list=[agent.email],
                ),
                daemon=True,
            ).start()
            CompanyActivityLog.objects.create(
                company=company,
                action='Agent Onboarded'
            )
            messages.success(request, 'Agent has been successfully onboarded.')
            if 'HTTP_REFERER' in request.META:
                return redirect(request.META['HTTP_REFERER'])  
            else:
                messages.error(request, 'Unable to redirect. Please try again.')
                return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def generate_invite_link(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.error(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')

    try:
        company = CompanyInformation.objects.get(user_id=request.user.id)
        if company.user_id != request.user.id:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')

        if request.method == 'POST':
            form = InviteLinkForm(request.POST)

            if form.is_valid():
                # Convert the admin's choice expiration into an integer
                hours = int(form.cleaned_data['expiry_duration'])

                max_uses = form.cleaned_data['max_uses']

                # Calculate the exact expiry datetime from now
                expires_at = timezone.now() + timedelta(hours=hours)

                # Create the InviteLink row — invite_token is auto-generated by the model
                invite = InviteLink.objects.create(
                    company=company,
                    expires_at=expires_at,
                    max_uses=max_uses,
                )

                invite_url = request.build_absolute_uri(
                    reverse('agent:join_via_invite') + f'?token={invite.invite_token}'
                )

                # Log it
                CompanyActivityLog.objects.create(
                    company=company,
                    action=f'Invite link generated (expires in {hours}h)'
                )

                # Pass the generated URL back to the template for the copy button
                messages.success(request, 'Invite link generated successfully. You can copy it from the panel below.')
                return redirect('company:manage-company')

        else:
            # GET request — just show the empty form
            form = InviteLinkForm()

        return render(request, 'estate/generate_invite.html', {'form': form})

    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})




def revoke_invite_link(request, token):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.warning(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    
    try:
        invite_link=InviteLink.objects.get(invite_token=token)
        company=CompanyInformation.objects.get(user_id=request.user.id)
        
        if invite_link.company!=company:
            messages.error(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        invite_link.is_active=False
        invite_link.save()
        CompanyActivityLog.objects.create(
            company=company,
            action='Invite Link Deactivated'
        )
        
        messages.success(request, 'The invite link has been successfully revoked.')
        return redirect('company:manage-company')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def remove_agent(request, agent_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.warning(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)
        employee=Employees.objects.get(agent_uuid=agent_uuid)
        if not employee.company == company:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        agent=AgentInformation.objects.get(agent_uuid=agent_uuid)
        #handing every property and lead data they got during their stay in the company back to the company
        PropertyManagementRent.objects.filter(agent_uuid=agent.agent_uuid, company_uuid=company.unique_company_id).update(agent_uuid=None,user_id=request.user.id)
        PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid, company_uuid=company.unique_company_id).update(agent_uuid=None, user_id=request.user.id)
        LeadInfo.objects.filter(agent_id=agent.agent_uuid, company_uuid=company.unique_company_id).update(agent_id=None)
        Appointments.objects.filter(agent_uuid=agent.agent_uuid, company_uuid=company.unique_company_id).update(agent_uuid=None)
        agent.company_uuid = None
        agent.save()
        
        # Send email to agent (background thread)
        threading.Thread(
            target=send_estate_email,
            kwargs=dict(
                subject=f"Update on your status with {company.company_name}",
                template_name='emails/agent_removed_notification.html',
                context={'agent': agent.users, 'company': company, 'request': request},
                recipient_list=[agent.email],
            ),
            daemon=True,
        ).start()

        employee.delete()
        messages.success(request, 'Agent has been successfully removed from the company.')
        CompanyActivityLog.objects.create(
            company=company,
            action='Agent Deleted'
        )
        return redirect('company:manage-company')
    except ObjectDoesNotExist:
        messages.error(request, 'Agent data could not be found.')
        return redirect('company:manage-company')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
    




def edit_employee(request, agent_uuid):

    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('landing')
    if request.user.role != 'company':
        messages.warning(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    company = get_object_or_404(CompanyInformation, user_id=request.user.id)

    employee = get_object_or_404(Employees,agent_uuid=agent_uuid,company=company)

    # ── 3. Handle form submission (POST) ───────────────────────────────────
    if request.method == 'POST':
        form = EditEmployeeForm(request.POST,instance=employee)

        if form.is_valid():
            form.save()
            messages.success(request,f"Details for {employee.agent_name} have been updated successfully.")
            return redirect('company:edit-employee', agent_uuid=agent_uuid)

        else:
            messages.error(request,'Please correct the errors in the form.')

    # ── 4. Handle page load (GET) ──────────────────────────────────────────
    else:
        # Pre-fill the form with the employee's current data
        form = EditEmployeeForm(instance=employee)

    return render(request, 'company/edit_employee.html', {
        'form':          form,
        'employee':      employee,
        'company':       company,
        'base_template': 'company/base.html',  # matches your extends pattern
    })


def company_feedbacks(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role != 'company':
        messages.info(request, 'Access denied: This page is for company accounts only.')
        return redirect('landing')
    
    try:
        company_uuid = CompanyInformation.objects.filter(user_id=request.user.id).values_list('unique_company_id', flat=True).first()
        company_rating = CompanyRating.objects.filter(company_uuid=company_uuid)
        avg_rating = company_rating.aggregate(Avg('rating'))['rating__avg'] or 0

        return render(request, 'company/company_feedbacks.html', {
            'feedback': company_rating,
            'avg_rating': avg_rating,
        })
    
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})