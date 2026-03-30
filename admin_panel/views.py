from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.forms import *
from django.http import HttpResponseRedirect, JsonResponse
from django.db import transaction
from companies.models import CompanyInformation, CompanyActivityLog
from agents.models import AgentInformation
from estate.models import LeadInfo
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from core.utils import *
from django.utils.http import url_has_allowed_host_and_scheme
from agents.forms import AgentInformationForm, SocialLinksFormSet, ExperienceFormSet
from members.models import User
from django.utils import timezone
from core.models import PropertyManagementRent, PropertyManagementSale, PropertyViews, Appointments, ErrorLog
from agents.quotes import get_random_quote
from django.db.models import Sum, Avg, Count,Q
from core.utils import monthly_change, engagement_rate, total_agents_engagement_calculator
from django.urls import reverse
from companies.forms import SocialLinksFormset, CompanyForm,JobPostForm, InviteLinkForm, EditEmployeeForm
from .models import *
from datetime import date, timedelta
from django.core.paginator import Paginator
from core.utils import *
import traceback
from estate.models import *
from estate.forms import *
from members.forms import UpdateUserForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from core import news_scrape as ns
from estate.filters import *
from core.models import *
import uuid
from core.utils import refresh_activity_score
from itertools import chain
from django.views.decorators.csrf import ensure_csrf_cookie




def admin_dashboard(request):
    # ... your auth checks here ...

    now = timezone.now()
    today = date.today()
    one_week_ago = now - timedelta(days=7)

    # ─────────────────────────────────────────────────────────────────────
    # 1. USER STATS — 1 query (aggregate everything in one hit)
    # ─────────────────────────────────────────────────────────────────────
    user_stats = User.objects.aggregate(
        total=Count('id'),
        customer_count=Count('id', filter=Q(role='customer')),
        agent_count=Count('id', filter=Q(role='agent')),
        company_count=Count('id', filter=Q(role='company')),
        new_this_week=Count('id', filter=Q(date_joined__gte=one_week_ago)),
    )

    total_users     = user_stats['total']
    total_customers = user_stats['customer_count']
    total_agents    = user_stats['agent_count']
    total_companies = user_stats['company_count']
    new_this_week   = user_stats['new_this_week']

    # ─────────────────────────────────────────────────────────────────────
    # 2. AGENTS — 2 queries (one aggregate, one slice)
    # ─────────────────────────────────────────────────────────────────────
    agent_stats = AgentInformation.objects.aggregate(
        # Rename 'verified' to 'verified_count'
        verified_count=Count('id', filter=Q(verified=True)),
        # Rename 'unverified' to 'unverified_count'
        unverified_count=Count('id', filter=Q(verified=False)),
    )

    # Then access them like this:
    verified_agents = agent_stats['verified_count']
    pending_agent_count = agent_stats['unverified_count']
    verified_agents_pct = (verified_agents / total_agents * 100) if total_agents else 0

    pending_agent_list = AgentInformation.objects.filter(verified=False)[:5]

    # ─────────────────────────────────────────────────────────────────────
    # 3. COMPANIES — 2 queries (one aggregate, one slice)
    # ─────────────────────────────────────────────────────────────────────
    company_stats = CompanyInformation.objects.aggregate(
        verified_count=Count('id', filter=Q(verified=True)),
        unverified_count=Count('id', filter=Q(verified=False)),
        starter=Count('id', filter=Q(company_tier='starter')),
        growth=Count('id', filter=Q(company_tier='growth')),
        enterprise=Count('id', filter=Q(company_tier='enterprise')),
    )
    verified_companies     = company_stats['verified_count']
    pending_company_count  = company_stats['unverified_count']
    verified_companies_pct = (verified_companies / total_companies * 100) if total_companies else 0
    starter_companies      = company_stats['starter']
    growth_companies       = company_stats['growth']
    enterprise_companies   = company_stats['enterprise']

    pending_company_list = CompanyInformation.objects.filter(verified=False)[:5]

    pending_verifications = pending_agent_count + pending_company_count

    # ─────────────────────────────────────────────────────────────────────
    # 4. PROPERTIES — 2 queries (one aggregate each model)
    # ─────────────────────────────────────────────────────────────────────
    sale_stats = PropertyManagementSale.objects.aggregate(
        total=Count('id'),
        live=Count('id', filter=Q(is_listed=True)),
        flagged=Count('id', filter=Q(flagged=True)),
        residential=Count('id', filter=Q(property_category='Residential')),
        commercial=Count('id', filter=Q(property_category='Commercial')),
        land=Count('id', filter=Q(property_category='Land')),
        new_this_week=Count('id', filter=Q(listed_date__gte=one_week_ago)),
    )
    rent_stats = PropertyManagementRent.objects.aggregate(
        total=Count('id'),
        live=Count('id', filter=Q(is_listed=True)),
        flagged=Count('id', filter=Q(flagged=True)),
        residential=Count('id', filter=Q(property_category='Residential')),
        commercial=Count('id', filter=Q(property_category='Commercial')),
        land=Count('id', filter=Q(property_category='Land')),
        new_this_week=Count('id', filter=Q(listed_date__gte=one_week_ago)),
    )

    total_sale        = sale_stats['total']
    total_rent        = rent_stats['total']
    total_properties  = total_sale + total_rent
    live_listings     = sale_stats['live'] + rent_stats['live']
    stored_listings   = total_properties - live_listings
    live_listings_pct = (live_listings / total_properties * 100) if total_properties else 0
    flagged_listings  = sale_stats['flagged'] + rent_stats['flagged']
    residential_count = sale_stats['residential'] + rent_stats['residential']
    commercial_count  = sale_stats['commercial']  + rent_stats['commercial']
    land_count        = sale_stats['land']        + rent_stats['land']
    new_listings_this_week = sale_stats['new_this_week'] + rent_stats['new_this_week']

    # Recent listings — combine both querysets, sort in Python (avoids UNION complexity)
    # 2 queries
    recent_sale = list(PropertyManagementSale.objects.order_by('-listed_date')[:8])
    recent_rent = list(PropertyManagementRent.objects.order_by('-listed_date')[:8])

    # Keep as model instances so template properties like .base_image and .residential work correctly.
    recent_listings = sorted(
        chain(recent_sale, recent_rent),
        key=lambda x: x.listed_date,
        reverse=True
    )[:8]

    # ─────────────────────────────────────────────────────────────────────
    # 5. INQUIRIES — 1 query (aggregate) + 1 slice
    # ─────────────────────────────────────────────────────────────────────
    inquiry_stats = LeadInfo.objects.aggregate(
        total=Count('id'),
        today=Count('id', filter=Q(date_created=today)),
    )
    total_inquiries     = inquiry_stats['total']
    new_inquiries_today = inquiry_stats['today']
    recent_inquiries    = LeadInfo.objects.order_by('-date_created')[:6]

    # ─────────────────────────────────────────────────────────────────────
    # 6. PARTNERSHIPS — 1 query (aggregate) + 1 slice
    # ─────────────────────────────────────────────────────────────────────
    partnership_stats = Partnership.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
    )
    total_partnerships   = partnership_stats['total']
    pending_partnerships = partnership_stats['pending']
    recent_partnerships  = Partnership.objects.order_by('-created_at')[:5]

    # ─────────────────────────────────────────────────────────────────────
    # 7. REVIEWS — 2 queries, merged in Python
    # ─────────────────────────────────────────────────────────────────────
    agent_name_map = {
        a.agent_uuid: f"{a.first_name} {a.last_name}"
        for a in AgentInformation.objects.only('agent_uuid', 'first_name', 'last_name')
    }
    company_name_map = {
        c.unique_company_id: c.company_name
        for c in CompanyInformation.objects.only('unique_company_id', 'company_name')
    }

    recent_agent_reviews = AgentRating.objects.select_related('user').order_by('-created_at')[:6]
    recent_company_reviews = CompanyRating.objects.select_related('user').order_by('-created_at')[:6]

    recent_reviews = []
    for r in recent_agent_reviews:
        recent_reviews.append({
            'user': r.user,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at,
            'source': 'Agent',
            'target_uuid': r.agent_uuid,
            'target_name': agent_name_map.get(r.agent_uuid, 'Unknown Agent'),
        })
    for r in recent_company_reviews:
        recent_reviews.append({
            'user': r.user,
            'rating': r.rating,
            'comment': r.comment,
            'created_at': r.created_at,
            'source': 'Company',
            'target_uuid': r.company_uuid,
            'target_name': company_name_map.get(r.company_uuid, 'Unknown Company'),
        })

    recent_reviews = sorted(
        recent_reviews,
        key=lambda x: x['created_at'],
        reverse=True
    )[:6]

    # ─────────────────────────────────────────────────────────────────────
    # 8. RECENT SIGNUPS — 1 query
    # ─────────────────────────────────────────────────────────────────────
    recent_signups = User.objects.order_by('-date_joined')[:8]

    # ─────────────────────────────────────────────────────────────────────
    # 9. TOP AGENTS — counts from both sale + rent flows
    # ─────────────────────────────────────────────────────────────────────
    sale_counts = PropertyManagementSale.objects.values('agent_uuid').annotate(count=Count('id'))
    rent_counts = PropertyManagementRent.objects.values('agent_uuid').annotate(count=Count('id'))

    agent_listing_counts = {}
    for item in sale_counts:
        if item['agent_uuid']:
            agent_listing_counts[item['agent_uuid']] = agent_listing_counts.get(item['agent_uuid'], 0) + item['count']
    for item in rent_counts:
        if item['agent_uuid']:
            agent_listing_counts[item['agent_uuid']] = agent_listing_counts.get(item['agent_uuid'], 0) + item['count']

    top_agent_uuids = sorted(agent_listing_counts, key=lambda k: agent_listing_counts[k], reverse=True)[:5]

    top_agents = []
    for agent_uuid in top_agent_uuids:
        agent = AgentInformation.objects.filter(agent_uuid=agent_uuid).first()
        if not agent:
            continue
        top_agents.append({
            'agent': agent,
            'listing_count': agent_listing_counts.get(agent_uuid, 0),
        })


    # ─────────────────────────────────────────────────────────────────────
    # CONTEXT
    # ─────────────────────────────────────────────────────────────────────
    context = {
        # Users
        'total_users':               total_users,
        'total_customers':           total_customers,
        'total_agents':              total_agents,
        'total_companies':           total_companies,
        'new_users_this_week':       new_this_week,

        # Agent verification
        'verified_agents':           verified_agents,
        'verified_agents_pct':       round(verified_agents_pct, 1),
        'pending_agent_verifications': pending_agent_count,
        'pending_agent_list':        pending_agent_list,

        # Company verification
        'verified_companies':        verified_companies,
        'verified_companies_pct':    round(verified_companies_pct, 1),
        'pending_company_verifications': pending_company_count,
        'pending_company_list':      pending_company_list,

        # Combined verification
        'pending_verifications':     pending_verifications,

        # Properties
        'total_properties':          total_properties,
        'total_sale':                total_sale,
        'total_rent':                total_rent,
        'live_listings':             live_listings,
        'stored_listings':           stored_listings,
        'live_listings_pct':         round(live_listings_pct, 1),
        'flagged_listings':          flagged_listings,
        'residential_count':         residential_count,
        'commercial_count':          commercial_count,
        'land_count':                land_count,
        'new_listings_this_week':    new_listings_this_week,
        'recent_listings':           recent_listings,

        # Inquiries
        'total_inquiries':           total_inquiries,
        'new_inquiries_today':       new_inquiries_today,
        'recent_inquiries':          recent_inquiries,

        # Partnerships
        'total_partnerships':        total_partnerships,
        'pending_partnerships':      pending_partnerships,
        'recent_partnerships':       recent_partnerships,

        # Reviews
        'recent_reviews':            recent_reviews,

        # Company tiers
        'starter_companies':         starter_companies,
        'growth_companies':          growth_companies,
        'enterprise_companies':      enterprise_companies,

        # Users
        'recent_signups':            recent_signups,

        # Top agents
        'top_agents':                top_agents,

        # Misc
        'today':                     today,
    }

    return render(request, 'executive/admin_dashboard.html', context)


@ensure_csrf_cookie
def agent_verification(request, agent_uuid):
    try:
        AgentInformation.objects.filter(agent_uuid=agent_uuid).update(verified=True)
        messages.success(request, 'Agent Verified')
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect('executive:admin-dashboard')
    except ObjectDoesNotExist:
        messages.error(request, 'Company Doesnt exists')
    except:
        messages.error(request, 'An Error Occured')
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})

@ensure_csrf_cookie
def company_verification(request, company_uuid):
    try:
        CompanyInformation.objects.filter(unique_company_id=company_uuid).update(verified=True)
        messages.success(request, 'Company Verified')
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect('executive:admin-dashboard')
    except ObjectDoesNotExist:
        messages.error(request, 'Company Doesnt exists')
    except:
        messages.error(request, 'An Error Occured')
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def suspend_account(request):
    pass