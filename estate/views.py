from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.contrib import messages
from members.forms import UpdateUserForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from core import news_scrape as ns
from django.core.paginator import Paginator
from .filters import *
from django.db import transaction
from admin_panel.views import admin
from members.models import User
from companies.models import CompanyInformation, CompanyAnalytics
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from agents.models import AgentInformation
from core.models import *








# Algorithm for adding properties to the wishlist
def wishlist_generator(properties_list, user_id):
    if properties_list[0].property_type == 'Rent':
        user_wishlists=WishlistStorageUnit.objects.filter(user_id=user_id).filter(property_type='Rent')
    else:
        user_wishlists=WishlistStorageUnit.objects.filter(user_id=user_id).filter(property_type='Sale')
        
    properties_id=[]
    for prop in properties_list:
        properties_id.append(prop.id)
    user_wishlist_list=[]
    for i in user_wishlists:
        i=i.property_id
        user_wishlist_list.append(i)
    boolean_results=[]
    for k in properties_id:
        if k in user_wishlist_list:
            boolean_results.append(True)
        else:
            boolean_results.append(False)
    return boolean_results





#list for all properties on sale
def buy_property(request):
    if request.user.is_authenticated:
        if request.user.role != 'customer':
            messages.info(request, 'Only Customers can buy properties')
            return redirect('landing')
        try:
            
            sale_qs=PropertyManagementSale.objects.all().order_by('-listed_date')
            #pagination and listings
            myfilter=PropertySaleFilter(request.GET, queryset=sale_qs)
            sale_qs=myfilter.qs
            #The line that does the actual querying and its organized by the date listed from the latest to the oldest 
            p=Paginator(sale_qs, 9)
            page=request.GET.get('page')
            on_sale= p.get_page(page)
            nums= "a" * on_sale.paginator.num_pages
            
            properties_list=[]
            for prop in sale_qs:
                properties_list.append(prop)
            in_wishlist=wishlist_generator(properties_list, request.user.id)
            properties_with_wishist=zip(on_sale, in_wishlist)
            
            return render(request, 'estate/buy_property.html', {'buy': properties_with_wishist,'nums':nums, 'salefilter':myfilter})
        
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.info(request, ('Join us Now to start'))
        return redirect('login')


#list of all leased property
def rent_property(request):
        if request.user.is_authenticated:
            if request.user.role != 'customer':
                messages.info(request, 'Only Customers can buy properties')
                return redirect('landing')
            try:
                
                rent_qs=PropertyManagementRent.objects.all().order_by('-listed_date')
                #pagination and listing
                myfilter=PropertyRentFilter(request.GET, queryset=rent_qs)
                rent_qs=myfilter.qs
                p=Paginator(rent_qs, 9)
                page= request.GET.get('page')
                on_lease= p.get_page(page)
                nums= "a" * on_lease.paginator.num_pages
                
                properties_list=[]
                for prop in rent_qs:
                    properties_list.append(prop)
                in_wishlist=wishlist_generator(properties_list, request.user.id)
                properties_with_wishlist=zip(on_lease, in_wishlist)
                return render(request, 'estate/rent_property.html', {'nums':nums, 'on_lease': properties_with_wishlist, 'rentfilter':myfilter})
            
            except Exception as e:
                print(f'ERROR IS{e}')
                return render(request, 'estate/error_page.html', {'e': e})
            
        else:
            messages.info(request, ('Join Estate Web Now!!!'))
            return redirect('login')




#full details of listed property
def view_property_on_sale(request, property_id):
    if request.user.is_authenticated:
        if request.user.role != 'customer':
            messages.info(request, 'Only Customers can view properties on sale')
            return redirect('landing')
        try:
            property= PropertyManagementSale.objects.get(pk=property_id)
            property_image=property.images.all()
            email=request.user.email #contact information
            #checking if owner of listing is an estate agent
            if property.company_uuid:
                company_handled=CompanyInformation.objects.get(unique_company_id=property.company_uuid)
                company_info=company_handled
                messages.info(request, f'Listing Is handled by {company_handled.company_name}')
                return render(request, 'estate/view_property_s.html', {'property':property,'images':property_image, 
                                                                'email':email, 'company_info':company_info})
            elif property.agent_uuid != 'None':
                agent_handled=AgentInformation.objects.get(user_id=property.user_id)
                messages.info(request, f'Listing Is handled by a universal agent')
                return render(request, 'estate/view_property_s.html', {'property':property,'images':property_image, 
                                                                'agent_info':agent_handled, 'email':email})
        
            else:
                messages.info(request, 'Listing Is handled by the home owner')
                return render(request, 'estate/view_property_s.html', {'property':property, 'email':email})
        
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


#Full details of listing
def view_property_on_lease(request, property_id):
    if request.user.is_authenticated:
        if request.user.role != 'customer':
            messages.info(request, 'Only Customers can view properties on lease')
            return redirect('landing')
        try:
            email=request.user.email#contact information
            property= PropertyManagementRent.objects.get(pk=property_id)
            property_images= property.images.all()
            if property.company_uuid != 'None':
                company_handled=CompanyInformation.objects.get(unique_company_id=property.company_uuid)
                company_info=company_handled
                messages.info(request, f'Listing Is handled by {company_handled.company_name}')
                return render(request, 'estate/view_property_r.html', {'property':property,'images':property_images, 
                                                                'email':email, 'company_info':company_info})
            elif property.agent_uuid != 'None':
                agent_handled=AgentInformation.objects.get(user_id=property.user_id)
                
                messages.info(request, f'Listing Is handled by a universal agent')
                return render(request, 'estate/view_property_r.html', {'property':property,'images':property_images, 
                                                                'agent_info':agent_handled, 'email':email})
        
            else:
                messages.info(request, 'Listing Is handled by the home owner')
                return render(request, 'estate/view_property_r.html', {'property':property, 'email':email})
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')





'''User Handling Views'''

#view handling the users profile settings
def user_profile(request):
    print(request.user.role)
    try:
        if request.user.is_authenticated:
            if request.user.role != 'customer':
                messages.info(request, 'Different account different profile')
                return redirect('landing')
            try:
                info= AgentInformation.objects.get(user_id=request.user.id) #needed for django template in html side
                return render(request, 'estate/user_profile.html', {'headline': ns.article_headline, 'info':info})#news headline is passed
            
            except AgentInformation.DoesNotExist:
                    return render(request, 'estate/user_profile.html', {'headline': ns.article_headline})
                
        else:
            messages.warning(request, ('You need to be logged in to accesss this page'))
            return redirect('landing')
        
    except Exception as e:
        print(e)


#view handling users listings
def listed_properties(request):
    if request.user.is_authenticated:
        try:
            
            model= request.user.id
            #filtering the listings using both the users id and the properties id(Hacked my way through this🤡)
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
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


#view for toggling the on and off of my wishlist
def toggle_wishlist_rent(request, property_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to be logged in to access this page.")
        return redirect('landing')
    if request.user.role != 'customer':
        messages.info(request, 'Only Customers can save properties')
        return redirect('landing')
    try:
        wishlist_storage=WishlistStorageUnit.objects.filter(user_id=request.user.id, property_id=property_id, property_type="Rent")
        if wishlist_storage.exists():
            wishlist_storage.delete()
            like_decrement=PropertyManagementRent.objects.get(pk=property_id)
            like_decrement.total_likes=like_decrement.total_likes - 1
            like_decrement.save()
            messages.success(request, 'Property Removed From Wishlist')
        else:
            favourite=WishlistStorageUnit.objects.create(
                user_id=request.user.id,
                property_id=property_id,
                property_type="Rent"
            )
            favourite.save()
            like_increment=PropertyManagementRent.objects.get(pk=property_id)
            like_increment.total_likes=like_increment.total_likes + 1
            like_increment.save()
            messages.success(request, 'Property Added to wishlist')
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])  
        else:
            return redirect('customer:rent-property')
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})


#view for toggling the on and off of my wishlist
def toggle_wishlist_buy(request, property_id):
    if not request.user.is_authenticated:
        
        messages.warning(request, "You need to be logged in to access this page.")
        return redirect('landing')
    if request.user.role != 'customer':
        messages.info(request, 'Only Customers can save properties')
        return redirect('landing')
    try:
        wishlist_storage= WishlistStorageUnit.objects.filter(user_id=request.user.id, property_id=property_id, property_type="Sale")
        if wishlist_storage.exists():
            wishlist_storage.delete()
            like_decrement=PropertyManagementSale.objects.get(pk=property_id)
            like_decrement.total_likes=like_decrement.total_likes - 1
            like_decrement.save()
            messages.success(request, 'Property Removed From wishlist')
        else:
            favourite=WishlistStorageUnit.objects.create(
                user_id=request.user.id,
                property_id=property_id,
                property_type="Sale"
            )
            favourite.save()
            like_increment=PropertyManagementSale.objects.get(pk=property_id)
            like_increment.total_likes=like_increment.total_likes + 1
            like_increment.save()
            messages.success(request, 'Property Added Successfully')
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])  
        else:
            return redirect('customer:buy-property')
    
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})


#View listing all the users wishlist
def wishlist(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to be logged in to access this page.")
        return redirect('landing')
    if request.user.role != 'customer':
        messages.info(request, 'Access Denied(Customers Only)')
        return redirect('landing')
    try:
        #fetching the related forign key object in a single query
        wishlist_rent = WishlistStorageUnit.objects.filter(user_id=request.user.id, property_type="Rent")
        wishlist_sale = WishlistStorageUnit.objects.filter(user_id=request.user.id, property_type="Sale")
        
        rent_list=[]
        for i in wishlist_rent:
            i=i.property_id
            on_lease=PropertyManagementRent.objects.get(pk=i)
            rent_list.append(on_lease)
        sale_list=[]
        for i in wishlist_sale:
            i=i.property_id
            on_sale=PropertyManagementSale.objects.get(pk=i)
            sale_list.append(on_sale)
        
        
        #Total items in wishlist
        total_saved = wishlist_rent.count() + wishlist_sale.count()
        context = {
            'wishlist_rent': zip(wishlist_rent, rent_list),
            'wishlist_sale': zip(wishlist_sale, sale_list),
            'total_saved': total_saved,
        }
        return render(request, 'estate/wishlist.html', context)
    
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})


#view handling update of user profile
def update_profile(request, user_id):
    if request.user.is_authenticated:
        if request.user.role != 'customer':
            messages.info(request, 'Customers account only')
            return redirect('landing')
        try:
            #could have done it in the urls but leave it here
            formatted_user_id= int(user_id)
            
            #making sure only a user can edit his/her property
            if formatted_user_id == request.user.id:
                #The Users data is being pulled out from the database using their id
                profile= User.objects.get(pk=user_id)
                form= UpdateUserForm(request.POST or None, request.FILES or None, instance=profile)
                
                if form.is_valid():
                    form.save()
                    return redirect('customer:user-profile')
                
                else:
                    messages.error(request, 'check If you made any errors')
                return render(request, 'estate/update_profile.html', {'profile': profile, 'form': form})
            
            else:
                messages.warning(request, 'Youre not allowed to access this page')
                return redirect('customer:user-profile')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


#view to change passoword
def change_password(request):
    if request.user.is_authenticated:
        if request.user.role != 'customer':
            messages.info(request, 'Stop messing around')
            return redirect('landing')
        try:
            
            if request.method == 'POST':
                form= PasswordChangeForm(request.user, request.POST)
                
                if form.is_valid():
                    new_pass=form.save()
                    #the new password set is then encrypted, updated and saved 
                    update_session_auth_hash(request, new_pass)
                    messages.success(request, 'Password has been Changed successfully')
                    return redirect('customer:password-success')
                
                else:
                    messages.error(request, 'There was an error changing your password.... please try again..')
                    return redirect('customer:change-password')
                
            else:
                form= PasswordChangeForm(request.user)
                return render(request, 'estate/change_passw.html', {'form': form})
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.info(request, 'You have to be logged in to access this page')
        return redirect('landing')


#success page after password change
def change_password_success(request):
    if request.user.is_authenticated:
        if request.user.role != 'customer':
            messages.info(request, 'Congrats after messing around youve seen the green button')
        try:
            return render(request, 'estate/succ_pass.html')
        
        except Exception as e:
            print(f'ERROR IS {e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, 'You need to be logged in to access this page')
        return redirect('landing')


#Users Settings
def profile_settings(request):
    if request.user.is_authenticated:
        if request.user.role != 'customer':
            messages.info(request, 'Access Denied customer account only')
            return redirect('landing')
        try:
            return render(request, 'estate/settings.html', {})
        
        except Exception as e:
            print(f'ERROR IS {e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, 'You need to be logged in to access this page')
        return redirect('landing')



#deleting user and all associated data 
def delete_account(request):
    if request.user.is_authenticated:
        if request.user.role != 'customer':
            messages.info(request, 'Stop messing around')
            return redirect('landing')
        try:
            #getting all that needs to be deleted if a users account was actually deleted
            property1= PropertyManagementRent.objects.filter(user_id=request.user.id)
            property2= PropertyManagementSale.objects.filter(user_id=request.user.id)
            agent_info=AgentInformation.objects.filter(user_id=request.user.id)
            
            
            user_id=User.objects.get(pk=request.user.id)
            
            #A try block to catch any error while deleting the account if not delete account
            try:
                property1.delete()
                property2.delete()
                user_id.delete()
                agent_info.delete()
                
            except Exception as e:
                messages.error(request, 'There was an error, Try again later.....')
                print(e)
                return redirect('customer:user-profile')
            messages.success(request, 'Account has been deleted Successfully')
            return redirect('landing')
        
        except Exception as e:
            print(f'ERROR IS {e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.info(request, 'You have to be logged in to access this page')
        return redirect('landing')


#estate aget profile view
def estate_agent_profile(request, agent_id):
    if request.user.is_authenticated:
        try:
            #all the agents information
            agent_info= AgentInformation.objects.get(user_id=agent_id)
            agent_experience= agent_info.experiences.all()
            agent_social= agent_info.social.all()
            return render(request, 'estate/agent_profile.html', {'information': agent_info,
                                                                'experience':agent_experience,
                                                                'network': agent_social})
        except Exception as e:
            print(e)
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.info('You have to be logged in to access this page')
        return redirect('landing')





def inquiry_form_rent(request, property_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Log in to send inquires')
        return redirect('landing')
    
    if not request.user.role == 'customer':
        messages.success(request, 'Only customer account can send Inquiries')
        return redirect('landing')
    
    try:
        submitted=False
        on_rent=PropertyManagementRent.objects.get(pk=property_id)
        if request.method=='POST':
            inq_form=InquiryForm(request.POST or None)
            if inq_form.is_valid():
                if on_rent.company_uuid:
                    inq_form=inq_form.save(commit=False)
                    inq_form.company_uuid=on_rent.company_uuid
                    inq_form.property_intrested=on_rent.id
                    inq_form.agent_id=on_rent.agent_uuid
                    inq_form.property_type='Rent'
                    inq_form.property_name=on_rent.house_type
                    inq_form.date_created=date.today()
                    inq_form.save()
                    return HttpResponseRedirect('?submitted=True')
                else:
                    inq_form.save()
            
        else:
            inq_form= InquiryForm()
            
            if 'submitted' in request.GET:
                submitted=True
                
        return render(request, 'estate/inq_form.html', {'form':inq_form, 'submitted': submitted})
    except Exception as e:
        return render(request, 'estate/error_page.html', {e})





def inquiry_form_sale(request, property_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Log in to send inquires')
        return redirect('landing')
    
    if not request.user.role == 'customer':
        messages.success(request, 'Only customer account can send Inquiries')
        return redirect('landing')
    
    try:
        submitted=False
        on_sale=PropertyManagementSale.objects.get(pk=property_id)
        if request.method=='POST':
            inq_form=InquiryForm(request.POST or None)
            if inq_form.is_valid():
                if on_sale.company_uuid:
                    inq_form=inq_form.save(commit=False)
                    inq_form.company_uuid=on_sale.company_uuid
                    inq_form.property_intrested=on_sale.id
                    inq_form.agent_id=on_sale.agent_uuid
                    inq_form.property_type='Sale'
                    inq_form.property_name=on_sale.house_type
                    inq_form.date_created=date.today()
                    inq_form.save()
                    return HttpResponseRedirect('?submitted=True')
                else:
                    inq_form.save()
            
        else:
            inq_form= InquiryForm()
            
            if 'submitted' in request.GET:
                submitted=True
                
        return render(request, 'estate/inq_form.html', {'form':inq_form, 'submitted': submitted})
    except Exception as e:
        return render(request, 'estate/error_page.html', {e})