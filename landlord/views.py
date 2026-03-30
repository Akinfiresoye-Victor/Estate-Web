from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LandlordInformation
from .forms import LandlordInformationForm
from core.models import PropertyManagementRent, PropertyManagementSale, ErrorLog, PropertyViews, WishlistStorageUnit
from django.db import transaction
from django.db.models import Value, CharField
import traceback
import itertools
from estate.models import LeadInfo
from datetime import datetime, date
from django.db.models import Sum



"""
context = {
    'properties': Property.objects.filter(owner=request.user, is_active=True)[:4],
    'recent_inquiries': Inquiry.objects.filter(property__owner=request.user).order_by('-created_at')[:5],
    'active_listings_count': Property.objects.filter(owner=request.user, is_active=True).count(),
    'total_views': ...,  # aggregate sum of views across landlord's properties
    'total_saves': ...,  # aggregate sum of wishlist saves
    'unread_inquiry_count': Inquiry.objects.filter(property__owner=request.user, is_read=False).count(),
}
"""
def dashboard(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if not request.user.role == 'landlord':
        messages.info(request, 'Landlord Account Only')
        return redirect('landing')
    try:
        landlord = LandlordInformation.objects.get(user_id=request.user.id)
        property_on_sale=PropertyManagementSale.objects.filter(landlord_uuid=landlord.landlord_uuid)
        property_on_lease=PropertyManagementRent.objects.filter(landlord_uuid=landlord.landlord_uuid)
        # Fetch each type with only 2 rows — annotate so template can identify type
        sale_qs = (
            property_on_sale
            .annotate(listing_type=Value('Sale', output_field=CharField()))
            .order_by('-time_stamp')[:2]
        )
        rent_qs = (
            property_on_lease
            .annotate(listing_type=Value('Rent', output_field=CharField()))
            .order_by('-time_stamp')[:2]
        )

        # Single flat list: up to 4 properties (2 sale + 2 rent), interleaved
        properties = list(itertools.chain(sale_qs, rent_qs))

        active_listings_count = (
            PropertyManagementSale.objects.filter(landlord_uuid=landlord.landlord_uuid, is_listed=True).count()
            + PropertyManagementRent.objects.filter(landlord_uuid=landlord.landlord_uuid, is_listed=True).count()
        )
        inquiries = LeadInfo.objects.filter(landlord_id=landlord.landlord_uuid)
        recent_inquiries=inquiries.order_by('-date_created')[:5]
        total_views = PropertyViews.objects.filter(uuid=landlord.landlord_uuid).count()
        rent_likes = property_on_lease.aggregate(total=Sum('total_likes'))['total'] or 0
        sale_likes = property_on_sale.aggregate(total=Sum('total_likes'))['total'] or 0
        total_likes = rent_likes + sale_likes

        return render(request, 'landlord/dashboard.html', {
            'landlord': landlord,
            'properties': properties,
            'active_listings_count': active_listings_count,
            'inquiries_count':inquiries.count(),
            'recent_inquiries': recent_inquiries,
            'total_views': total_views,
            'total_saves': total_likes,
        })
    
    except LandlordInformation.DoesNotExist:
        messages.info(request, 'Please complete your landlord profile to continue.')
        return redirect('landlord:profile-setup')
    except Exception as e:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})

def inventory(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'landlord':
        messages.info(request, 'Landlord Account Only')
        return redirect('landing')
    try:
        landlord = LandlordInformation.objects.get(user_id=request.user.id)
        
        sales = PropertyManagementSale.objects.filter(landlord_uuid=landlord.landlord_uuid).order_by('-time_stamp')
        rentals = PropertyManagementRent.objects.filter(landlord_uuid=landlord.landlord_uuid).order_by('-time_stamp')
        
        context = {
            'landlord': landlord,
            'sales': sales,
            'rentals': rentals,
            'total_limit': landlord.inventory_slots,
            'live_limit': landlord.listing_slots,
            'used_slots': sales.count() + rentals.count()
        }
        return render(request, 'landlord/inventory.html', context)
        
    except LandlordInformation.DoesNotExist:
        messages.error(request, 'Landlord profile not found.')
        return redirect('landing')
    except Exception as e:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})

def profile_setup(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'landlord':
        messages.info(request, 'Landlord Account Only')
        return redirect('landing')
    
    try:
        # If profile exists, redirect to dashboard
        if LandlordInformation.objects.filter(user_id=request.user.id).exists():
            return redirect('landlord:dashboard')
        if request.method == 'POST':
            form = LandlordInformationForm(request.POST, request.FILES)
            if form.is_valid():
                with transaction.atomic():
                    landlord = form.save(commit=False)
                    landlord.user = request.user
                    landlord.user_id = request.user.id
                    landlord.first_name = request.user.first_name
                    landlord.last_name = request.user.last_name
                    landlord.email = request.user.email
                    landlord.save()
                    
                    messages.success(request, 'Profile completed successfully! Welcome to Estate Web.')
                    return redirect('landlord:dashboard')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = LandlordInformationForm()
            
        return render(request, 'landlord/profile_setup.html', {'form': form})
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def lanlord_profile(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'landlord':
        messages.info(request, 'Landlord Account Only')
        return redirect('landing')
    try:
        landlord = LandlordInformation.objects.get(user_id=request.user.id)
        return render(request, 'landlord/profile.html', {'landlord': landlord})
    except LandlordInformation.DoesNotExist:
        messages.error(request, 'Landlord profile not found.')
        return redirect('landing')
    except Exception as e:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})