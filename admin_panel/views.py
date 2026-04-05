from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q
from itertools import chain
import time
from datetime import date, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django_ratelimit.decorators import ratelimit

from .decorators import admin_required
from .forms import AdminLoginForm
from .models import AdminAccessLog

from members.models import User
from agents.models import AgentInformation
from companies.models import CompanyInformation
from landlord.models import LandlordInformation
from core.models import PropertyManagementSale, PropertyManagementRent
from estate.models import LeadInfo
from core.utils import score_new_listing, refresh_activity_score


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

@ratelimit(key='ip', rate='5/10m', block=False)
def admin_login(request):
    if getattr(request, 'limited', False):
        from django.http import HttpResponse
        return HttpResponse('Too many login attempts. Please try again later.', status=429)

    if request.user.is_authenticated and request.user.is_staff and request.session.get('_admin_authenticated'):
        return redirect('control_panel:dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.user_cache
            login(request, user)
            request.session['_admin_authenticated'] = True
            request.session.set_expiry(3600 * 8)  # session expires in 8 hours
            AdminAccessLog.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                action='LOGIN_SUCCESS',
            )
            return redirect('control_panel:dashboard')
        else:
            time.sleep(2)
            AdminAccessLog.objects.create(
                ip_address=get_client_ip(request),
                action='LOGIN_FAILED',
                notes=f'Attempted username: {request.POST.get("username")}'
            )
            error = 'Invalid credentials.'
            return render(request, 'control_panel/login.html', {'form': form, 'error': error})
    else:
        form = AdminLoginForm(request=request)
    return render(request, 'control_panel/login.html', {'form': form})

@admin_required
@require_POST
def admin_logout(request):
    AdminAccessLog.objects.create(
        user=request.user,
        ip_address=get_client_ip(request),
        action='LOGOUT',
    )
    if '_admin_authenticated' in request.session:
        del request.session['_admin_authenticated']
    logout(request)
    return redirect('control_panel:login')

@admin_required
def dashboard(request):
    today = date.today()
    one_week_ago = timezone.now() - timedelta(days=7)

    # 1. USER STATS 
    user_stats = User.objects.aggregate(
        total=Count('id'),
        customer_count=Count('id', filter=Q(role='customer')),
        agent_count=Count('id', filter=Q(role='agent')),
        company_count=Count('id', filter=Q(role='company')),
        landlord_count=Count('id', filter=Q(role='landlord')),
    )

    suspended_users = User.objects.filter(is_active=False).count()

    # 2. AGENTS & COMPANIES 
    unverified_agents = AgentInformation.objects.filter(verified=False).count()
    unverified_companies = CompanyInformation.objects.filter(verified=False).count()

    # 3. PROPERTIES 
    sale_stats = PropertyManagementSale.objects.aggregate(
        total=Count('id'),
        live=Count('id', filter=Q(is_listed=True)),
        flagged=Count('id', filter=Q(flagged=True)),
    )
    rent_stats = PropertyManagementRent.objects.aggregate(
        total=Count('id'),
        live=Count('id', filter=Q(is_listed=True)),
        flagged=Count('id', filter=Q(flagged=True)),
    )

    total_sale = sale_stats['total']
    total_rent = rent_stats['total']
    total_properties = total_sale + total_rent
    live_listings = sale_stats['live'] + rent_stats['live']
    inventory_listings = total_properties - live_listings
    flagged_listings = sale_stats['flagged'] + rent_stats['flagged']
    
    # Recent Logs
    recent_logs = AdminAccessLog.objects.all()[:10]

    context = {
        'total_users': user_stats['total'],
        'total_customers': user_stats['customer_count'],
        'total_agents': user_stats['agent_count'],
        'total_companies': user_stats['company_count'],
        'total_landlords': user_stats['landlord_count'],
        'suspended_users': suspended_users,
        'unverified_agents': unverified_agents,
        'unverified_companies': unverified_companies,
        'total_properties': total_properties,
        'total_sale': total_sale,
        'total_rent': total_rent,
        'live_listings': live_listings,
        'inventory_listings': inventory_listings,
        'flagged_listings': flagged_listings,
        'recent_logs': recent_logs,
    }

    return render(request, 'control_panel/dashboard.html', context)

@admin_required
def users(request):
    users_qs = User.objects.all().order_by('-date_joined')
    
    # Filters
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    if role_filter:
        users_qs = users_qs.filter(role=role_filter)
    if status_filter == 'active':
        users_qs = users_qs.filter(is_active=True)
    elif status_filter == 'suspended':
        users_qs = users_qs.filter(is_active=False)
    if search_query:
        users_qs = users_qs.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query))

    paginator = Paginator(users_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'control_panel/users.html', {'page_obj': page_obj})

@admin_required
def user_detail(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    return render(request, 'control_panel/user_detail.html', {'target_user': target_user})

@admin_required
@require_POST
def suspend_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user.is_superuser:
        messages.error(request, "Cannot suspend a superuser.")
        return redirect('control_panel:user_detail', user_id=target_user.id)

    reason = request.POST.get('reason', 'No reason provided')
    
    if target_user.is_active:
        target_user.is_active = False
        action_msg = 'USER_SUSPENDED'
    else:
        target_user.is_active = True
        action_msg = 'USER_UNSUSPENDED'

    target_user.save()

    AdminAccessLog.objects.create(
        user=request.user,
        ip_address=get_client_ip(request),
        action=action_msg,
        target_type='user',
        target_id=str(target_user.id),
        notes=f'Reason or intent: {reason}'
    )
    
    return redirect('control_panel:user_detail', user_id=target_user.id)

@admin_required
@require_POST
def delete_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    confirm_username = request.POST.get('confirm_username')
    
    if target_user.is_superuser:
        messages.error(request, "Cannot delete superuser.")
        return redirect('control_panel:users')

    if confirm_username != target_user.username:
        messages.error(request, "Confirmation username did not match!")
        return redirect('control_panel:user_detail', user_id=target_user.id)

    user_info = f"{target_user.username} ({target_user.email}) [{target_user.role}]"
    
    # Pre-clean the related profiles explicitly
    if target_user.role == 'agent':
        AgentInformation.objects.filter(user_id=target_user.id).delete()
    elif target_user.role == 'company':
        CompanyInformation.objects.filter(user_id=target_user.id).delete()
    elif target_user.role == 'landlord':
        LandlordInformation.objects.filter(user_id=target_user.id).delete()

    # Once profile is cleaned, safely delete the main user record
    target_user.delete()

    AdminAccessLog.objects.create(
        user=request.user,
        ip_address=get_client_ip(request),
        action='USER_DELETED',
        target_type='user',
        target_id=str(user_id),
        notes=f'Deleted user: {user_info}'
    )
    messages.success(request, f"User {confirm_username} permanently deleted.")
    return redirect('control_panel:users')

@admin_required
def agents(request):
    agents_qs = AgentInformation.objects.all().order_by('-agent_uuid')
    
    is_verified = request.GET.get('verified', '')
    is_solo = request.GET.get('solo', '')
    search = request.GET.get('search', '')

    if is_verified == 'yes':
        agents_qs = agents_qs.filter(verified=True)
    elif is_verified == 'no':
        agents_qs = agents_qs.filter(verified=False)
    
    if is_solo == 'yes':
        agents_qs = agents_qs.filter(Q(company_uuid__isnull=True) | Q(company_uuid=''))
    elif is_solo == 'no':
        agents_qs = agents_qs.exclude(Q(company_uuid__isnull=True) | Q(company_uuid=''))

    if search:
        agents_qs = agents_qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))

    paginator = Paginator(agents_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'control_panel/agents.html', {'page_obj': page_obj})

@admin_required
def agent_detail(request, agent_uuid):
    agent = get_object_or_404(AgentInformation, agent_uuid=agent_uuid)
    listings_count = PropertyManagementSale.objects.filter(agent_uuid=agent_uuid).count() + PropertyManagementRent.objects.filter(agent_uuid=agent_uuid).count()
    return render(request, 'control_panel/agent_detail.html', {'agent': agent, 'listings_count': listings_count})

@admin_required
@require_POST
def toggle_agent_verified(request, agent_uuid):
    agent = get_object_or_404(AgentInformation, agent_uuid=agent_uuid)
    
    agent.verified = not agent.verified
    agent.save()
    
    action = 'AGENT_VERIFIED' if agent.verified else 'AGENT_UNVERIFIED'
    
    AdminAccessLog.objects.create(
        user=request.user,
        ip_address=get_client_ip(request),
        action=action,
        target_type='agent',
        target_id=agent_uuid,
    )
    return redirect('control_panel:agent_detail', agent_uuid=agent_uuid)

@admin_required
def companies(request):
    companies_qs = CompanyInformation.objects.all().order_by('-date_joined')
    
    is_verified = request.GET.get('verified', '')
    tier = request.GET.get('tier', '')

    if is_verified == 'yes':
        companies_qs = companies_qs.filter(verified=True)
    elif is_verified == 'no':
        companies_qs = companies_qs.filter(verified=False)
    
    if tier:
        companies_qs = companies_qs.filter(company_tier=tier)

    paginator = Paginator(companies_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'control_panel/companies.html', {'page_obj': page_obj})

@admin_required
def company_detail(request, company_id):
    company = get_object_or_404(CompanyInformation, unique_company_id=company_id)
    agents_list = AgentInformation.objects.filter(company_uuid=company_id)
    listings_count = PropertyManagementSale.objects.filter(company_uuid=company_id).count() + PropertyManagementRent.objects.filter(company_uuid=company_id).count()
    return render(request, 'control_panel/company_detail.html', {'company': company, 'agents_list': agents_list, 'listings_count': listings_count})

@admin_required
@require_POST
def toggle_company_verified(request, company_id):
    company = get_object_or_404(CompanyInformation, unique_company_id=company_id)
    company.verified = not company.verified
    company.save()
    
    action = 'COMPANY_VERIFIED' if company.verified else 'COMPANY_UNVERIFIED'
    AdminAccessLog.objects.create(
        user=request.user,
        ip_address=get_client_ip(request),
        action=action,
        target_type='company',
        target_id=company_id,
    )
    return redirect('control_panel:company_detail', company_id=company_id)

@admin_required
@require_POST
def change_company_tier(request, company_id):
    company = get_object_or_404(CompanyInformation, unique_company_id=company_id)
    new_tier = request.POST.get('tier')
    
    if new_tier in ['starter', 'growth', 'enterprise']:
        old_tier = company.company_tier
        company.company_tier = new_tier
        company.save()
        
        AdminAccessLog.objects.create(
            user=request.user,
            ip_address=get_client_ip(request),
            action='COMPANY_TIER_CHANGED',
            target_type='company',
            target_id=company_id,
            notes=f'Changed from {old_tier} to {new_tier}'
        )
    return redirect('control_panel:company_detail', company_id=company_id)

@admin_required
def listings(request):
    # Query Filter Extraction
    f_type = request.GET.get('type', '')
    f_status = request.GET.get('status', '')
    f_feat = request.GET.get('featured', '')
    f_flagged = request.GET.get('flagged', '')
    f_cat = request.GET.get('category', '')
    search = request.GET.get('search', '')

    # Define the common fields we need for the template
    # Note: Sale has 'price' and Rent has 'price_range'. We'll alias them.
    common_fields = [
        'id', 'location', 'state', 'is_listed', 'listed_date', 
        'property_category', 'residential', 'commercial', 'lands',
        'listing_score', 'featured_listings', 'flagged', 'is_flagged', 'property_type'
    ]

    def _apply_filters(qs):
        if f_status == 'listed': qs = qs.filter(is_listed=True)
        elif f_status == 'inventory': qs = qs.filter(is_listed=False)
        
        if f_feat == 'yes': qs = qs.filter(featured_listings=True)
        elif f_feat == 'no': qs = qs.filter(featured_listings=False)

        if f_flagged == 'yes': qs = qs.filter(flagged=True)
        elif f_flagged == 'no': qs = qs.filter(flagged=False)

        if f_cat: qs = qs.filter(property_category=f_cat)
        
        if search:
            qs = qs.filter(
                Q(location__icontains=search) | 
                Q(state__icontains=search) | 
                Q(residential__icontains=search) | 
                Q(commercial__icontains=search) | 
                Q(lands__icontains=search)
            )
        return qs

    sale_qs = _apply_filters(PropertyManagementSale.objects.all()).values(*common_fields)
    rent_qs = _apply_filters(PropertyManagementRent.objects.all()).values(*common_fields)

    if f_type == 'sale':
        combined_qs = sale_qs.order_by('-listed_date')
    elif f_type == 'rent':
        combined_qs = rent_qs.order_by('-listed_date')
    else:
        # Use union to combine them at the DB level
        combined_qs = sale_qs.union(rent_qs).order_by('-listed_date')

    paginator = Paginator(combined_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'control_panel/listings.html', {'page_obj': page_obj})

@admin_required
def listing_detail(request, type, pk):
    if type not in ('sale', 'rent'):
        from django.http import Http404
        raise Http404
    if type == 'sale':
        listing = get_object_or_404(PropertyManagementSale, pk=pk)
    else:
        listing = get_object_or_404(PropertyManagementRent, pk=pk)
    
    agent = AgentInformation.objects.filter(agent_uuid=listing.agent_uuid).first() if listing.agent_uuid else None
    
    logs = AdminAccessLog.objects.filter(target_type=f'listing_{type}', target_id=str(pk))
    
    return render(request, 'control_panel/listing_detail.html', {'listing': listing, 'type': type, 'agent': agent, 'logs': logs})

@admin_required
@require_POST
def force_unlist(request, type, pk):
    if type not in ('sale', 'rent'):
        from django.http import Http404
        raise Http404
    model = PropertyManagementSale if type == 'sale' else PropertyManagementRent
    listing = get_object_or_404(model, pk=pk)
    listing.is_listed = False
    listing.save()
    
    AdminAccessLog.objects.create(user=request.user, ip_address=get_client_ip(request), action='LISTING_UNLISTED', target_type=f'listing_{type}', target_id=str(pk))
    return redirect('control_panel:listing_detail', type=type, pk=pk)

@admin_required
@require_POST
def toggle_feature(request, type, pk):
    if type not in ('sale', 'rent'):
        from django.http import Http404
        raise Http404
    model = PropertyManagementSale if type == 'sale' else PropertyManagementRent
    listing = get_object_or_404(model, pk=pk)
    
    listing.featured_listings = not listing.featured_listings
    listing.save()
    
    # Recalculate scoring as requested
    prop_type_str = 'Sale' if type == 'sale' else 'Rent'
    refresh_activity_score(listing, prop_type_str, force=True)

    action = 'LISTING_FEATURED' if listing.featured_listings else 'LISTING_UNFEATURED'
    AdminAccessLog.objects.create(user=request.user, ip_address=get_client_ip(request), action=action, target_type=f'listing_{type}', target_id=str(pk))
    return redirect('control_panel:listing_detail', type=type, pk=pk)

@admin_required
@require_POST
def toggle_flag(request, type, pk):
    if type not in ('sale', 'rent'):
        from django.http import Http404
        raise Http404
    model = PropertyManagementSale if type == 'sale' else PropertyManagementRent
    listing = get_object_or_404(model, pk=pk)
    
    listing.flagged = not listing.flagged
    listing.save()

    action = 'LISTING_FLAGGED' if listing.flagged else 'LISTING_UNFLAGGED'
    AdminAccessLog.objects.create(user=request.user, ip_address=get_client_ip(request), action=action, target_type=f'listing_{type}', target_id=str(pk))
    return redirect('control_panel:listing_detail', type=type, pk=pk)

@admin_required
@require_POST
def delete_listing(request, type, pk):
    if type not in ('sale', 'rent'):
        from django.http import Http404
        raise Http404
    model = PropertyManagementSale if type == 'sale' else PropertyManagementRent
    listing = get_object_or_404(model, pk=pk)
    
    # Try identifying by name correctly
    c_name = listing.residential or listing.commercial or listing.lands or "Unknown"

    confirm_name = request.POST.get('confirm_name')
    if confirm_name != c_name:
        messages.error(request, "Confirmation name did not match!")
        return redirect('control_panel:listing_detail', type=type, pk=pk)
        
    listing.delete()
    AdminAccessLog.objects.create(user=request.user, ip_address=get_client_ip(request), action='LISTING_DELETED', target_type=f'listing_{type}', target_id=str(pk), notes=f'Permanently deleted property {c_name}')
    
    messages.success(request, f"Listing deleted.")
    return redirect('control_panel:listings')

@admin_required
def access_log(request):
    logs = AdminAccessLog.objects.all()
    
    f_action = request.GET.get('action')
    search = request.GET.get('search')
    
    if f_action: logs = logs.filter(action=f_action)
    if search: logs = logs.filter(Q(user__username__icontains=search) | Q(ip_address__icontains=search))
        
    paginator = Paginator(logs, 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'control_panel/access_log.html', {'page_obj': page_obj})