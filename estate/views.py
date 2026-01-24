from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
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




'''Algorithms Start👇'''

def wishlist_generator(properties_list, user_id):
    
    """
    Takes in a list of indexes and returns the boolean output based on 
    favourited properties of each users
    """
    if properties_list:
        if properties_list[0].property_type == 'Rent':
            user_wishlists=WishlistStorageUnit.objects.filter(user_id=user_id, property_type='Rent')
        else:
            user_wishlists=WishlistStorageUnit.objects.filter(user_id=user_id, property_type='Sale')
        properties_id=[]
        user_wishlist_list=[]
        boolean_results=[]
        
        for prop in properties_list:
            properties_id.append(prop.id)
            
        for raw_wishlist in user_wishlists:
            user_wishlist_list.append(raw_wishlist.property_id)
            
        for k in properties_id:
            if k in user_wishlist_list:
                boolean_results.append(True)
            else:
                boolean_results.append(False)
        return boolean_results
    else:
        boolean_results =[]
        return boolean_results



def property_view_count(property_id, property_type, users_id, users_uuid):
    """
    Tracks Property Views
    """
    all_views=PropertyViews.objects.filter(property_type=property_type, property_id=property_id)
    viewers_id=[]
    for users in all_views:
        all_viewers_id=users.user_id
        viewers_id.append(all_viewers_id)
    if not users_id in viewers_id:
        new_object=PropertyViews.objects.create(
            user_id=users_id,
            property_type=property_type,
            property_id=property_id,
            uuid=users_uuid
        )
        new_object.save()

'''Algorithms End👆 '''



def buy_property(request):
    
    """
    Lists all the properties on sale
    """
    
    if not request.user.is_authenticated:
        messages.info(request,'Log in to gain access')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    
    try:
        sale_qs=PropertyManagementSale.objects.all().order_by('-listed_date')
        #Filtering Code
        myfilter=PropertySaleFilter(request.GET, queryset=sale_qs)
        if myfilter.qs:
            sale_qs=myfilter.qs
        else:
            sale_qs=[]
        #The line that does the actual querying and its organized by the date listed from the latest to the oldest 
        p=Paginator(sale_qs, 9)
        page=request.GET.get('page')
        on_sale= p.get_page(page)
        nums= "a" * on_sale.paginator.num_pages
        
        properties_list=[]
        for prop in sale_qs:
            properties_list.append(prop)
        #generating users liked properties
        in_wishlist=wishlist_generator(properties_list, request.user.id)
        properties_with_wishist=zip(on_sale, in_wishlist)
        context={
            'buy': properties_with_wishist,
            'on_sale': on_sale,
            'nums':nums,
            'salefilter':myfilter
        }
        return render(request, 'estate/buy_property.html',context)
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def rent_property(request):
    """
    Lists all the properties on rent
    """
    if not request.user.is_authenticated:
        messages.info(request, 'login Required')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    try:
        rent_qs=PropertyManagementRent.objects.all().order_by('-listed_date')
        #Filtering
        myfilter=PropertyRentFilter(request.GET, queryset=rent_qs)
        if myfilter.qs:
            rent_qs=myfilter.qs
        else:
            rent_qs=[]
        p=Paginator(rent_qs, 9)
        page= request.GET.get('page')
        on_lease= p.get_page(page)
        nums= "a" * on_lease.paginator.num_pages
        
        properties_list=[]
        for prop in rent_qs:
            properties_list.append(prop)
        in_wishlist=wishlist_generator(properties_list, request.user.id)
        properties_with_wishlist=zip(on_lease, in_wishlist)
        context={
            'nums':nums,
            'on_lease': properties_with_wishlist,
            'leased':on_lease,
            'rentfilter':myfilter
        }
        return render(request, 'estate/rent_property.html', context)
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def view_property_on_sale(request, property_id):
    """
    View Listed Property in details
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain access')
        return redirect('login')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'

        property_to_be_viewed= PropertyManagementSale.objects.get(pk=property_id)
        try:
            company_in_charge=CompanyInformation.objects.get(user_id=property_to_be_viewed.user_id)
            agent_in_charge=None
            property_view_count(property_id, "Sale", request.user.id,company_in_charge.unique_company_id)
        except CompanyInformation.DoesNotExist:
            agent_in_charge= AgentInformation.objects.get(user_id=property_to_be_viewed.user_id)
            company_in_charge=None
            property_view_count(property_id, "Sale", request.user.id, agent_in_charge.agent_uuid)
        context={
            'property': property_to_be_viewed,
            'agent_info': agent_in_charge,
            'company_info': company_in_charge,
            'base_template':base_template,
            'role':user_role
        }
        return render(request, 'estate/view_property_s.html', context)
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})



def view_property_on_lease(request, property_id):
    """
    View Listed Property in details
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain access')
        return redirect('login')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'

        property_to_be_viewed= PropertyManagementRent.objects.get(pk=property_id)
        
        try:
            company_in_charge=CompanyInformation.objects.get(user_id=property_to_be_viewed.user_id)
            agent_in_charge=None
            property_view_count(property_id, "Rent", request.user.id, company_in_charge.unique_company_id)
            messages.info(request, 'Cooperate Listing')
        except CompanyInformation.DoesNotExist:
            agent_in_charge= AgentInformation.objects.get(user_id=property_to_be_viewed.user_id)
            messages.info(request, 'Agent Listing')
            company_in_charge=None
            property_view_count(property_id, "Rent", request.user.id, agent_in_charge.agent_uuid)
        context={
            'property': property_to_be_viewed,
            'agent_info': agent_in_charge,
            'company_info': company_in_charge,
            'base_template':base_template,
            'role':user_role,
        }
        return render(request, 'estate/view_property_r.html', context)
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})





def user_profile(request):
    """
    Users Landing Page
    """
    try:
        if not request.user.is_authenticated:
            messages.info(request, 'login Required')
            return redirect('login')
        if not request.user.role == 'customer':
            messages.error(request, 'Different account different profile')
            return redirect('landing')
        return render(request, 'estate/user_profile.html', {'headline': ns.article_headline})
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})



'''
    """Landlord Logic.... Coming Soon
    """
def listed_properties(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to g ain access')
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
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})'''




def toggle_wishlist_rent(request, property_id):
    """
    Toggling ON/OFF Favourite for property on lease
    """
    if not request.user.is_authenticated:
        messages.info(request, "Log in to gain access")
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    try:
        wishlist_storage=WishlistStorageUnit.objects.filter(user_id=request.user.id, property_id=property_id, property_type="Rent")
        if wishlist_storage.exists():
            wishlist_storage.delete()
            property_like_decrement=PropertyManagementRent.objects.get(pk=property_id)
            property_like_decrement.total_likes-=1
            property_like_decrement.save()
            messages.success(request, 'Property Removed From wishlist')
        else:
            favourite=WishlistStorageUnit.objects.create(
                user_id=request.user.id,
                property_id=property_id,
                property_type="Rent"
            )
            favourite.save()
            property_like_increment=PropertyManagementRent.objects.get(pk=property_id)
            property_like_increment.total_likes+=1
            property_like_increment.save()
            messages.success(request, 'Property Added to wishlist')
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])  
        else:
            return redirect('customer:rent-property')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def toggle_wishlist_buy(request, property_id):
    """
    Toggling ON/OFF Favourite for property on sale
    """
    if not request.user.is_authenticated:
        messages.info(request, "Log in to gain access")
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    try:
        wishlist_storage= WishlistStorageUnit.objects.filter(user_id=request.user.id, property_id=property_id, property_type="Sale")
        if wishlist_storage.exists():
            wishlist_storage.delete()
            property_like_decrement=PropertyManagementSale.objects.get(pk=property_id)
            property_like_decrement.total_likes-=1
            property_like_decrement.save()
            messages.success(request, 'Property Removed From wishlist')
        else:
            favourite=WishlistStorageUnit.objects.create(
                user_id=request.user.id,
                property_id=property_id,
                property_type="Sale"
            )
            favourite.save()
            property_like_increment=PropertyManagementSale.objects.get(pk=property_id)
            property_like_increment.total_likes+=1
            property_like_increment.save()
            messages.success(request, 'Property Added Successfully')
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])  
        else:
            return redirect('customer:buy-property')
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def wishlist(request):
    """
    Listing each users favourited property
    """
    if not request.user.is_authenticated:
        messages.info(request, "Log in to gain access")
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    try:
        wishlist_rent = WishlistStorageUnit.objects.filter(user_id=request.user.id, property_type="Rent")
        wishlist_sale = WishlistStorageUnit.objects.filter(user_id=request.user.id, property_type="Sale")
        
        rent_list=[]
        sale_list=[]
        for rent in wishlist_rent:
            rent=rent.property_id
            on_lease=PropertyManagementRent.objects.get(pk=rent)
            rent_list.append(on_lease)
        
        for sale in wishlist_sale:
            sale=sale.property_id
            on_sale=PropertyManagementSale.objects.get(pk=sale)
            sale_list.append(on_sale)
        
        total_saved = wishlist_rent.count() + wishlist_sale.count()
        context = {
            'wishlist_rent': zip(wishlist_rent, rent_list),
            'wishlist_sale': zip(wishlist_sale, sale_list),
            'lease_count': wishlist_rent.count(),
            'sale_count': wishlist_sale.count(),
            'total_saved': total_saved,
        }
        return render(request, 'estate/wishlist.html', context)
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def update_profile(request, user_id):
    """
    Update User Profile View
    Only The User can edit his/her own profile
    """
    if not request.user.is_authenticated:
        messages.info(request, 'log in to gain access')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customers account only')
        return redirect('landing')
    try:
        formatted_user_id= int(user_id)
        
        if not formatted_user_id == request.user.id:
            messages.warning(request, 'Access Denied')
            return redirect('landing')
    
        profile= User.objects.get(pk=user_id)
        if request.method == 'POST':
            
            form= UpdateUserForm(request.POST or None, request.FILES or None, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('customer:user-profile')
            else:
                messages.error(request, 'check for errors')
        else:
            form=UpdateUserForm(instance=profile)
        context={
            'profile': profile, 
            'form': form
        }
        return render(request, 'estate/update_profile.html',context)
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def change_password(request):
    """
    Change User Passwords with precise lines of code
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain acess')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    try:
        if request.method == 'POST':
            form= PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                new_pass=form.save() 
                update_session_auth_hash(request, new_pass)
                messages.success(request, 'Password Changed successfully')
                return redirect('customer:password-success')
            
            else:
                messages.error(request, 'Error Changing password...')
                return redirect('customer:change-password')
            
        else:
            form= PasswordChangeForm(request.user)
            return render(request, 'estate/change_passw.html', {'form': form})
        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def change_password_success(request):
    """
    Success Page after chaging password
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain access')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.info(request, 'Congrats after messing around youve seen the green button')
    try:
        return render(request, 'estate/succ_pass.html')
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def profile_settings(request):
    """
    User settings
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain access')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    try:
        return render(request, 'estate/settings.html')
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})
    




# FIXME This is an important issue
def delete_account(request):
    """
    Delete user account view
    """
    if not request.user.is_authenticated:
        messages.info(request, 'login Required')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    try:
        property1= PropertyManagementRent.objects.filter(user_id=request.user.id)
        property2= PropertyManagementSale.objects.filter(user_id=request.user.id)
        
        user_id=User.objects.get(pk=request.user.id)
        
        
        try:
            property1.delete()
            property2.delete()
            user_id.delete()
            
        except Exception as e:
            messages.error(request, 'There was an error, Try again later.....')
            return redirect('customer:user-profile')
        messages.success(request, 'Account has been deleted Successfully')
        return redirect('landing')
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})






def review_company(request, company_uuid):
    # Check if user is a customer
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can submit reviews')
        return redirect('company:company-profile', company_uuid=company_uuid)
    if not request.user.is_authenticated:
        messages.info(request, 'Login to gain access')
        return redirect('landing')
    try:
        company = get_object_or_404(CompanyInformation, unique_company_id=company_uuid)
        
        # Check if user has already reviewed
        existing_review = CompanyRating.objects.filter(
            company_uuid=company_uuid,
            user=request.user
        ).first()
        
        if existing_review:
            messages.warning(request, 'You have already reviewed this company')
            return redirect('company:company-profile', company_uuid=company_uuid)
        
        if request.method == 'POST':
            form = ReviewFormCompany(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.company_uuid = company.unique_company_id
                review.user = request.user
                
                # Ensure rating is between 1 and 5
                if not (1 <= review.rating <= 5):
                    messages.error(request, 'Rating must be between 1 and 5 stars')
                    return redirect('company:company-profile', company_uuid=company_uuid)
                
                review.save()
                messages.success(request, 'Thank you for your review!!!')
                return redirect('company:company-profile', company_uuid=company_uuid)
            else:
                messages.error(request, 'Please correct the errors below')
        
        return redirect('company:company-profile', company_uuid=company_uuid)
        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})


def review_agent(request, agent_uuid):
    """Handle agent review submission"""
    # Check role
    if hasattr(request.user, 'role') and request.user.role != 'customer':
        messages.error(request, 'Only Customers can submit reviews')
        return redirect('agent:agent-profile', agent_uuid=agent_uuid)
    
    # Check authentication
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    
    try:
        agent = get_object_or_404(AgentInformation, agent_uuid=agent_uuid)
        
        # Check for existing review
        existing_review = AgentRating.objects.filter(
            agent_uuid=agent_uuid,
            user=request.user
        ).first()
        
        if existing_review:
            messages.warning(request, 'Review already submitted')
            return redirect('agent:agent-profile', agent_uuid=agent_uuid)
        
        if request.method == 'POST':
            form = ReviewFormAgent(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.agent_uuid = agent.agent_uuid
                review.user = request.user
                
                # Validate rating range
                if not (1 <= review.rating <= 5):
                    messages.error(request, 'Rating must be between 1 and 5 stars')
                    return redirect('agent:agent-profile', agent_uuid=agent_uuid)
                
                review.save()
                messages.success(request, 'Thanks for your review!!!')
                return redirect('agent:agent-profile', agent_uuid=agent_uuid)
            else:
                messages.error(request, 'Please correct the errors below')
        
        return redirect('agent:agent-profile', agent_uuid=agent_uuid)
        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})





#TODO Answer inquiry questions 
def inquiry_form(request, property_type, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain access')
        return redirect('login')
    
    if request.user.role != 'customer':
        messages.error(request, 'Customer access only')
        return redirect('landing')
    
    try:
        submitted=False
        if property_type == 'Sale':
            asset= PropertyManagementSale.objects.get(pk=property_id)
        elif property_type == 'Rent':
            asset= PropertyManagementRent.objects.get(pk=property_id)
        else:
            messages.error(request, 'Something went wrong')
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
                inq_form.property_intrested=asset.id
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
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})

#todo make sure after a user ad something to wishlist it doesnt reload the page 