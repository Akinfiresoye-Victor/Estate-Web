from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.http import HttpResponseRedirect,JsonResponse
from django.contrib import messages
from members.forms import UpdateUserForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from core import news_scrape as ns
from django.core.paginator import Paginator
from .filters import *
from members.models import User
from datetime import date
from agents.models import AgentInformation, AgentRating
from core.models import *
from companies.models import CompanyInformation, CompanyRating
import uuid
from django.db.models import Avg, Count
from django.core.exceptions import ObjectDoesNotExist
from core.utils import refresh_activity_score
from django.urls import reverse
import traceback

'''Algorithms Start👇'''

def wishlist_generator(properties_list, user_id):
    """
    Takes a list of property objects and returns a list of booleans
    indicating whether each property is in the user's wishlist.
    """
    if not properties_list:
        return []

    property_type = properties_list[0].property_type

    if property_type not in ('Rent', 'Sale'):
        return []

    wishlisted_ids = set(WishlistStorageUnit.objects.filter(user_id=user_id,property_type=property_type).values_list('property_id', flat=True))

    return [prop.id in wishlisted_ids for prop in properties_list]



def property_view_count(property_id, property_type, users_id, users_uuid):
    """
    Tracks Property Views
    """
    all_views=set(PropertyViews.objects.filter(property_type=property_type, property_id=property_id).values_list('user_id', flat=True))
    if users_id not in all_views:
        PropertyViews.objects.create(
            user_id=users_id,
            property_type=property_type,
            property_id=property_id,
            uuid=users_uuid
        )   


def _wishlist_for_user(properties_list, user):
    """
    Returns a list of True/False for each property.
    If the user is not authenticated we return all False
    so the page renders fine without crashing on user.id == None.
    """
    if not user or not user.is_authenticated:
        return [False] * len(properties_list)
    return wishlist_generator(properties_list, user.id)


'''Algorithms End👆 '''



def buy_property(request):
    """
    Lists all properties on sale, ordered by listing score.
    Works for both authenticated and unauthenticated users.
    Unauthenticated users see all listings but hearts show as empty.
    """
    try:
        sale_qs = PropertyManagementSale.objects.filter(is_listed=True).order_by(
            '-listing_score', '-listed_date'
        )
 
        myfilter = PropertySaleFilter(request.GET, queryset=sale_qs)
        sale_qs  = myfilter.qs if myfilter.qs.exists() else PropertyManagementSale.objects.none()
 
        p       = Paginator(sale_qs, 9)
        page    = request.GET.get('page')
        on_sale = p.get_page(page)
        nums    = "a" * on_sale.paginator.num_pages
 
        properties_list          = list(on_sale)  # only paginated slice, not full qs
        in_wishlist              = _wishlist_for_user(properties_list, request.user)
        properties_with_wishlist = zip(on_sale, in_wishlist)
 
        context = {
            'buy':        properties_with_wishlist,
            'on_sale':    on_sale,
            'nums':       nums,
            'salefilter': myfilter,
        }
        return render(request, 'estate/buy_property.html', context)
 
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
 
 
# ─── rent_property ────────────────────────────────────────────────────────────
 
def rent_property(request):
    """
    Lists all rental properties, ordered by listing score.
    Works for both authenticated and unauthenticated users.
    """
    try:
        rent_qs = PropertyManagementRent.objects.filter(is_listed=True).order_by(
            '-listing_score', '-listed_date'
        )
 
        myfilter = PropertyRentFilter(request.GET, queryset=rent_qs)
        rent_qs  = myfilter.qs if myfilter.qs.exists() else PropertyManagementRent.objects.none()
 
        p        = Paginator(rent_qs, 9)
        page     = request.GET.get('page')
        on_lease = p.get_page(page)
        nums     = "a" * on_lease.paginator.num_pages
 
        properties_list          = list(on_lease)  # paginated slice only
        in_wishlist              = _wishlist_for_user(properties_list, request.user)
        properties_with_wishlist = zip(on_lease, in_wishlist)
 
        context = {
            'nums':       nums,
            'on_lease':   properties_with_wishlist,
            'leased':     on_lease,
            'rentfilter': myfilter,
        }
        return render(request, 'estate/rent_property.html', context)
 
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
 

# Add this import at the top of your views.py alongside the other scoring import:
#
#   from .scoring import score_new_listing, refresh_activity_score


def view_property_on_sale(request, property_id):
    """View Listed Property in detail"""
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.get_full_path()}")

    try:
        base_template = {
            'company': 'company/base.html',
            'agent':   'agent/base.html',
        }.get(request.user.role, 'estate/base.html')

        prop = PropertyManagementSale.objects.get(pk=property_id)

        # ── Resolve who listed the property ──────────────────
        try:
            company_in_charge = CompanyInformation.objects.get(user_id=prop.user_id)
            agent_in_charge   = (
                AgentInformation.objects.get(agent_uuid=prop.agent_uuid)
                if prop.agent_uuid != 'None' else None
            )
            view_id = company_in_charge.unique_company_id
            msg = (
                f'{company_in_charge.company_name} listing: {agent_in_charge.first_name} in charge'
                if agent_in_charge
                else f'Listed by {company_in_charge.company_name}'
            )

        except CompanyInformation.DoesNotExist:
            agent_in_charge   = AgentInformation.objects.get(user_id=prop.user_id)
            company_in_charge = (
                CompanyInformation.objects.get(unique_company_id=agent_in_charge.company_uuid)
                if agent_in_charge.company_uuid else None
            )
            view_id = agent_in_charge.agent_uuid
            msg = (
                f'Listed by {agent_in_charge.first_name} at {company_in_charge.company_name}'
                if company_in_charge
                else f'Listed by {agent_in_charge.first_name} (Independent)'
            )

        messages.info(request, msg)
        property_view_count(property_id, "Sale", request.user.id, view_id)
        refresh_activity_score(prop, 'Sale')

        return render(request, 'estate/view_property_s.html', {
            'property':      prop,
            'agent_info':    agent_in_charge,
            'company_info':  company_in_charge,
            'base_template': base_template,
            'role':          request.user.role,
        })

    except ObjectDoesNotExist:
        messages.error(request, 'This property is no longer available.')
        return redirect(request.META.get('HTTP_REFERER', 'customer:buy-property'))

    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def view_property_on_lease(request, property_id):
    """View Listed Property in detail"""
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.get_full_path()}")

    try:
        base_template = {
            'company': 'company/base.html',
            'agent':   'agent/base.html',
        }.get(request.user.role, 'estate/base.html')

        property_to_be_viewed = PropertyManagementRent.objects.get(pk=property_id)

        try:
            company_in_charge = CompanyInformation.objects.get(user_id=property_to_be_viewed.user_id)
            agent_in_charge   = (
                AgentInformation.objects.get(agent_uuid=property_to_be_viewed.agent_uuid)
                if property_to_be_viewed.agent_uuid != 'None' else None
            )
            view_id = company_in_charge.unique_company_id
            msg = (
                f'{company_in_charge.company_name} listing: {agent_in_charge.first_name} in charge'
                if agent_in_charge
                else f'Listed by {company_in_charge.company_name}'
            )

        except CompanyInformation.DoesNotExist:
            agent_in_charge   = AgentInformation.objects.get(user_id=property_to_be_viewed.user_id)
            company_in_charge = (
                CompanyInformation.objects.get(unique_company_id=agent_in_charge.company_uuid)
                if agent_in_charge.company_uuid else None
            )
            view_id = agent_in_charge.agent_uuid
            msg = (
                f'Listed by {agent_in_charge.first_name} at {company_in_charge.company_name}'
                if company_in_charge
                else f'Listed by {agent_in_charge.first_name} (Independent)'
            )

        messages.info(request, msg)
        property_view_count(property_id, "Rent", request.user.id, view_id)
        refresh_activity_score(property_to_be_viewed, 'Rent')

        return render(request, 'estate/view_property_r.html', {
            'property':      property_to_be_viewed,
            'agent_info':    agent_in_charge,
            'company_info':  company_in_charge,
            'base_template': base_template,
            'role':          request.user.role,
        })

    except ObjectDoesNotExist:
        messages.error(request, 'This property is no longer available.')
        return redirect(request.META.get('HTTP_REFERER', 'customer:rent-property'))

    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def user_profile(request):
    """
    Users Landing Page
    """
    try:
        if not request.user.is_authenticated:
            messages.info(request, 'Please sign in to access your profile.')
            return redirect('login')
        if not request.user.role == 'customer':
            messages.error(request, 'Access denied: Customer profile only.')
            return redirect('landing')
        return render(request, 'estate/user_profile.html', {'headline': ns.article_headline})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



'''
    """Landlord Logic.... Coming Soon
    """
def listed_properties(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to access your properties.')
        return redirect('login')
    try:
        model= request.user.id
        if request.user.username == admin:
            property1= PropertyManagementRent.objects.order_by('-listed_date')
            property2= PropertyManagementSale.objects.order_by('-listed_date')
            return render(request, 'estate/my_listings.html', {'property1':property1, 'property2':property2})
        else:
            property1= PropertyManagementRent.objects.filter(user_id=model).order_by('-listed_date')
            property2= PropertyManagementSale.objects.filter(user_id=model).order_by('-listed_date')
            return render(request, 'estate/my_listings.html', {'property1':property1, 'property2':property2})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})'''






def toggle_wishlist_rent(request, property_id):
    """
    Toggle wishlist for a rent property.
    Unauthenticated users are redirected to login with ?next= so they come
    straight back here after signing in.
    AJAX: returns JSON {"added": true/false}
    """
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'login_required'}, status=401)
        # Pass the current full path so the user returns here after login
        return redirect(f"{reverse('login')}?next={request.get_full_path()}")
 
    if not request.user.role == 'customer':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'forbidden'}, status=403)
        messages.error(request, 'Saving properties is exclusive to customers.')
        return redirect('landing')
 
    try:
        wishlist_qs = WishlistStorageUnit.objects.filter(
            user_id=request.user.id,
            property_id=property_id,
            property_type="Rent"
        )
 
        if wishlist_qs.exists():
            wishlist_qs.delete()
            prop = PropertyManagementRent.objects.get(pk=property_id)
            prop.total_likes = max(0, prop.total_likes - 1)
            prop.save(update_fields=['total_likes'])
            added = False
        else:
            WishlistStorageUnit.objects.create(
                user_id=request.user.id,
                property_id=property_id,
                property_type="Rent"
            )
            prop = PropertyManagementRent.objects.get(pk=property_id)
            prop.total_likes += 1
            prop.save(update_fields=['total_likes'])
            added = True
 
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'added': added, 'likes': prop.total_likes})
 
        return redirect(request.META.get('HTTP_REFERER', 'customer:rent-property'))
 
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
 
 
# ─── toggle_wishlist_buy ──────────────────────────────────────────────────────
 
def toggle_wishlist_buy(request, property_id):
    """
    Toggle wishlist for a sale property.
    Unauthenticated users are redirected to login with ?next=.
    AJAX: returns JSON {"added": true/false}
    """
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'login_required'}, status=401)
        return redirect(f"{reverse('login')}?next={request.get_full_path()}")
 
    if not request.user.role == 'customer':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'forbidden'}, status=403)
        messages.error(request, 'Access restricted to customer accounts.')
        return redirect('landing')
 
    try:
        wishlist_qs = WishlistStorageUnit.objects.filter(
            user_id=request.user.id,
            property_id=property_id,
            property_type="Sale"
        )
 
        if wishlist_qs.exists():
            wishlist_qs.delete()
            prop = PropertyManagementSale.objects.get(pk=property_id)
            prop.total_likes = max(0, prop.total_likes - 1)
            prop.save(update_fields=['total_likes'])
            added = False
        else:
            WishlistStorageUnit.objects.create(
                user_id=request.user.id,
                property_id=property_id,
                property_type="Sale"
            )
            prop = PropertyManagementSale.objects.get(pk=property_id)
            prop.total_likes += 1
            prop.save(update_fields=['total_likes'])
            added = True
 
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'added': added, 'likes': prop.total_likes})
 
        return redirect(request.META.get('HTTP_REFERER', 'customer:buy-property'))
 
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})

def wishlist(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.get_full_path()}")
    if not request.user.role == 'customer':
        messages.error(request, 'Access denied: Customer accounts only.')
        return redirect('landing')
    try:
        # Get the wishlisted property IDs for this user
        wishlist_rent_ids = WishlistStorageUnit.objects.filter(
            user_id=request.user.id,
            property_type="Rent"
        ).values_list('property_id', flat=True)

        wishlist_sale_ids = WishlistStorageUnit.objects.filter(
            user_id=request.user.id,
            property_type="Sale"
        ).values_list('property_id', flat=True)

        # Fetch all matching properties in one query each — no loop, no N+1
        rent_list = PropertyManagementRent.objects.filter(pk__in=wishlist_rent_ids)
        sale_list = PropertyManagementSale.objects.filter(pk__in=wishlist_sale_ids)

        lease_count = wishlist_rent_ids.count()
        sale_count = wishlist_sale_ids.count()

        context = {
            'rent_list':   rent_list,
            'sale_list':   sale_list,
            'lease_count': lease_count,
            'sale_count':  sale_count,
            'total_saved': lease_count + sale_count,
        }
        return render(request, 'estate/wishlist.html', context)

    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id}) 


def update_profile(request):
    """
    Update User Profile View
    Only The User can edit his/her own profile
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to update your profile.')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Profile updates are for customers only.')
        return redirect('landing')
    try:
        
    
        profile= User.objects.get(pk=request.user.id)
        if request.method == 'POST':
            
            form= UpdateUserForm(request.POST or None, request.FILES or None, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('customer:user-profile')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form=UpdateUserForm(instance=profile)
        context={
            'profile': profile, 
            'form': form
        }
        return render(request, 'estate/update_profile.html',context)
    
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def change_password(request):
    """
    Change User Passwords with precise lines of code
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to change your password.')
        return redirect('login')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        if request.method == 'POST':
            form= PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                new_pass=form.save() 
                update_session_auth_hash(request, new_pass)
                messages.success(request, 'Your password has been updated successfully.')
                return redirect('customer:password-success')
            
            else:
                messages.error(request, 'Unable to update password. Please try again.')
                return redirect('customer:change-password')
            
        else:
            form= PasswordChangeForm(request.user)
            return render(request, 'estate/change_passw.html', {'form': form, 'base_template':base_template})
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def change_password_success(request):
    """
    Success Page after chaging password
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        return render(request, 'estate/succ_pass.html', {'base_template': base_template})
    
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def profile_settings(request):
    """
    User settings
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Access denied: Customer accounts only.')
        return redirect('landing')
    try:
        return render(request, 'estate/settings.html')
    
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
    





def delete_account(request):
    """
    Delete user account view
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to delete your account.')
        return redirect('login')
    if request.user.role != 'customer':
        messages.error(request, 'Account deletion is for customers only.')
        return redirect('landing')
    try:
        
        user_id=User.objects.get(pk=request.user.id)
        if request.user != user_id:
            messages.warning(request, 'Security Alert: Unauthorized access attempt.')
            return redirect('landing')
        wishlists= WishlistStorageUnit.objects.filter(user_id=request.user.id)
        try:
            wishlists.delete()
            user_id.delete()
        except Exception:
            messages.error(request, 'Unable to process your request. Please try again later.')
            return redirect('customer:user-profile')
        messages.success(request, 'Your account has been successfully closed.')
        return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})






def review_company(request, company_uuid):
    # Check if user is a customer
    if request.user.role != 'customer':
        messages.error(request, 'Reviews are restricted to customer accounts.')
        return redirect('company:company-profile', company_uuid=company_uuid)
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to submit a review.')
        return redirect('landing')
    try:
        company = get_object_or_404(CompanyInformation, unique_company_id=company_uuid)
        
        # Check if user has already reviewed
        existing_review = CompanyRating.objects.filter(
            company_uuid=company_uuid,
            user=request.user
        ).first()
        
        if existing_review:
            messages.warning(request, 'You have already submitted a review for this company.')
            return redirect('company:company-profile', company_uuid=company_uuid)
        
        if request.method == 'POST':
            form = ReviewFormCompany(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.company_uuid = company.unique_company_id
                review.user = request.user
                
                # Ensure rating is between 1 and 5
                if not (1 <= review.rating <= 5):
                    messages.error(request, 'Please provide a rating between 1 and 5 stars.')
                    return redirect('company:company-profile', company_uuid=company_uuid)
                
                review.save()
                messages.success(request, 'Thank you for sharing your feedback!')
                return redirect('company:company-profile', company_uuid=company_uuid)
            else:
                messages.error(request, 'Please correct the errors in your review.')
        
        return redirect('company:company-profile', company_uuid=company_uuid)
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def review_agent(request, agent_uuid):
    """Handle agent review submission"""
    # Check role
    if hasattr(request.user, 'role') and request.user.role != 'customer':
        messages.error(request, 'Reviews are restricted to customer accounts.')
        return redirect('agent:agent-profile', agent_uuid=agent_uuid)
    
    # Check authentication
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    
    try:
        agent = get_object_or_404(AgentInformation, agent_uuid=agent_uuid)
        
        # Check for existing review
        existing_review = AgentRating.objects.filter(
            agent_uuid=agent_uuid,
            user=request.user
        ).first()
        
        if existing_review:
            messages.warning(request, 'You have already submitted a review for this agent.')
            return redirect('agent:agent-profile', agent_uuid=agent_uuid)
        
        if request.method == 'POST':
            form = ReviewFormAgent(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.agent_uuid = agent.agent_uuid
                review.user = request.user
                
                # Validate rating range
                if not (1 <= review.rating <= 5):
                    messages.error(request, 'Please provide a rating between 1 and 5 stars.')
                    return redirect('agent:agent-profile', agent_uuid=agent_uuid)
                
                review.save()
                messages.success(request, 'Thank you for sharing your feedback!')
                return redirect('agent:agent-profile', agent_uuid=agent_uuid)
            else:
                messages.error(request, 'Please correct the errors in your review.')
        
        return redirect('agent:agent-profile', agent_uuid=agent_uuid)
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})






def inquiry_form(request, property_type, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to send an inquiry.')
        return redirect('login')
    
    if request.user.role != 'customer':
        messages.error(request, 'Inquiries are restricted to customer accounts.')
        return redirect('landing')
    
    try:
        submitted=False
        if property_type == 'Sale':
            asset= PropertyManagementSale.objects.get(pk=property_id)
        elif property_type == 'Rent':
            asset= PropertyManagementRent.objects.get(pk=property_id)
        else:
            messages.error(request, 'An unexpected error occurred. Please try again.')
            return redirect('javascript:history.back()')
        if request.method == 'POST':
            inq_form= InquiryForm(request.POST or None)
            if inq_form.is_valid():
                inq_form= inq_form.save(commit=False)
                inq_form.lead_id=uuid.uuid4()
                if asset.company_uuid:
                    inq_form.company_uuid= asset.company_uuid
                    if inq_form.schedule_tour:
                        appointment= Appointments.objects.create(
                            company_uuid= asset.company_uuid,
                            appointment=inq_form.schedule_tour,
                            note="Reaching Client",
                            appointment_type='Buisness',
                            property_id=property_id,
                            property_type=asset.property_type,
                            lead_uuid=inq_form.lead_id
                        )
                        appointment.save()
                else:
                    inq_form.company_uuid= asset.agent_uuid
                    if inq_form.schedule_tour:
                        appointment= Appointments.objects.create(
                            agent_uuid= asset.agent_uuid,
                            appointment=inq_form.schedule_tour,
                            note="Reaching Client",
                            appointment_type='Buisness',
                            property_id=property_id,
                            property_type=asset.property_type,
                            lead_uuid=inq_form.lead_id
                        )
                        appointment.save()
                inq_form.property_intrested=asset.pk
                inq_form.agent_id=asset.agent_uuid
                inq_form.property_type=asset.property_type
                if asset.property_category == 'Residential':
                    inq_form.property_name=asset.residential
                elif asset.property_category == 'Commercial':
                    inq_form.property_name=asset.commercial
                else:
                    inq_form.property_name=asset.lands
                inq_form.date_created=date.today()
                
                inq_form.save()
                return HttpResponseRedirect('?submitted=True')
        else:
            inq_form=InquiryForm()
            
            if 'submitted' in request.GET:
                submitted=True
        
        return render(request, 'estate/inq_form.html', {'form':inq_form, 'submitted':submitted})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})




def flag_listing(request, property_id, property_type):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to report this listing.')
        return redirect('login')
    try:
        if property_type == 'Sale':
            onsale_property=PropertyManagementSale.objects.get(pk=property_id)
            all_reports=set(UsersSaleFlags.objects.filter(property=onsale_property).values_list('users_id', flat=True))
            if request.user.id not in all_reports:
                UsersSaleFlags.objects.create(
                    property=onsale_property,
                    users_id=request.user.id
                )
                onsale_property.flagged=True
                onsale_property.save()
                messages.success(request, 'Thank you for your report. We will review this listing shortly.')
            else:
                messages.error(request, 'This listing has already been reported.')
            if 'HTTP_REFERER' in request.META:
                return redirect(request.META['HTTP_REFERER'])  
            else:
                return redirect('landing')
        elif property_type == 'Rent':
            leased_property=PropertyManagementRent.objects.get(pk=property_id)
            all_reports=set(UsersLeaseFlags.objects.filter(property=leased_property).values_list('users_id', flat=True))
            if request.user.id not in all_reports:
                UsersLeaseFlags.objects.create(
                    property=leased_property,
                    users_id=request.user.id
                )
                leased_property.flagged=True
                leased_property.save()
                messages.success(request, 'Thank you for your report. We will review this listing shortly.')
            if 'HTTP_REFERER' in request.META:
                return redirect(request.META['HTTP_REFERER'])  
            else:
                return redirect('landing')
            
            
        else:
            messages.error(request, 'An error occurred while identifying the property type.')
            if 'HTTP_REFERER' in request.META:
                return redirect(request.META['HTTP_REFERER'])  
            else:
                return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def toggle_compare(request, property_type, property_id):
    """
    Adds or removes a property from the compare session list.
    property_type: 'sale' or 'rent'
    Max 3 properties allowed.
    AJAX only — returns JSON.
    """
    try:
        key = f'compare_{property_type}'
        ids = request.session.get(key, [])

        if property_id in ids:
            ids.remove(property_id)
            action = 'removed'
        else:
            if len(ids) >= 3:
                return JsonResponse({'error': 'max_reached',
                                    'message': 'You can only compare up to 3 properties.'}, status=400)
            ids.append(property_id)
            action = 'added'

        request.session[key] = ids
        request.session.modified = True

        return JsonResponse({
            'action':  action,
            'count':   len(ids),
            'type':    property_type,
        })
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def compare_properties(request):
    try:
        sale_ids  = request.session.get('compare_sale', [])
        rent_ids  = request.session.get('compare_rent', [])

        sale_props = list(PropertyManagementSale.objects.filter(id__in=sale_ids, is_listed=True))
        rent_props = list(PropertyManagementRent.objects.filter(id__in=rent_ids, is_listed=True))

        # Combine — you compare across types
        all_props = sale_props + rent_props

        return render(request, 'estate/compare_page.html', {
            'properties':  all_props,
            'base_template': 'estate/base.html',  # adjust per role
        })
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def clear_compare(request):
    try:
        request.session.pop('compare_sale', None)
        request.session.pop('compare_rent', None)
        return JsonResponse({'success': True})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})

#FIXME Customers cant see the error page due to the name of the folder being estate and not customer