from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LandlordInformation
from .forms import LandlordInformationForm
from core.models import PropertyManagementRent, PropertyManagementSale, ErrorLog
from django.db import transaction
import traceback

def dashboard(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if not request.user.role == 'landlord':
        messages.info(request, 'Landlord Account Only')
        return redirect('landing')
    try:
        landlord = LandlordInformation.objects.get(user_id=request.user.id)
        
        # Simple stats
        sales_count = PropertyManagementSale.objects.filter(landlord_uuid=landlord.landlord_uuid).count()
        rents_count = PropertyManagementRent.objects.filter(landlord_uuid=landlord.landlord_uuid).count()
        total_listings = sales_count + rents_count
        
        context = {
            'landlord': landlord,
            'total_listings': total_listings,
        }
        return render(request, 'landlord/dashboard.html', context)
    
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

