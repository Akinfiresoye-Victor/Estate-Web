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
from . import news_scrape as ns
from django.core.paginator import Paginator
from .filters import *
from django.db import transaction
from admin_panel.views import admin
from members.models import User
from companies.models import CompanyInformation, CompanyAnalytics
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist




'''News Blog Automation'''
def articles(request):
    if request.user.is_authenticated:
        try:
            #news headlines
            headlines= ns.bs.find('div', class_="blog-item-title")
            headlines=headlines.text
            #estate article content
            article= ns.bs.find('div', class_="blog-item-content e-content")
            article=article.text
            full_article= "https://www.nigeriahousingmarket.com/"
            return render(request,'estate/article.html', {'headline':headlines,
                                                        'article':article,
                                                        "full_article":full_article})
        except:
            messages.error(request, ns.error)
            return redirect('customer:user-profile')
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


'''Users Feedbacks'''
def feedbacks(request):
    if request.user.is_authenticated:
        try:
            submitted = False
            if request.method == 'POST':
                messages.success(request, 'Thanks For your feedback....')
                form = FeedbackForm(request.POST)
                if form.is_valid():
                    form.save()
                    submitted=True
                    return redirect('customer:feedback')
            else:
                form = FeedbackForm()
                if 'submitted' in request.GET:
                    submitted = True
            return render(request, 'estate/feedback.html', {'form': form, 'submitted': submitted})
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e}, {e})
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')





'''Property Management'''

#listing properties for sale
def sell_property(request):
    if request.user.is_authenticated:
        
        #user must have an email before he/she can list a property
        if (request.user.role == 'customer' and request.user.email) or (request.user.role == 'company' or request.user.role == 'agent'):
            
            try:
                
                submitted= False

                if request.method== 'POST':
                    prop_form=SellForm(request.POST or None, request.FILES or None)
                    image_form=SaleImageFormSet(request.POST or None, request.FILES or None)
                    if prop_form.is_valid() and image_form.is_valid():
                        
                        with transaction.atomic():
                            landlord= prop_form.save(commit=False)
                            try:
                                company= CompanyInformation.objects.get(user_id= request.user.id)
                                landlord.company_uuid= company.unique_company_id
                                landlord.user_id= request.user.id
                                landlord.time_stamp=timezone.now()
                                landlord.save()
                                image_form.instance=landlord
                                image_form.save()
                            except CompanyInformation.DoesNotExist:
                                landlord.user_id= request.user.id
                                landlord.time_stamp= 0
                                landlord.save()
                                image_form.instance=landlord
                                image_form.save()
                        return HttpResponseRedirect('?submitted=True')
                    
                else:
                    prop_form= SellForm()
                    image_form=SaleImageFormSet()
                    
                    if 'submitted' in request.GET:
                        submitted=True
                
                return render(request, 'estate/sell_property.html', {'form': prop_form,'image_form':image_form, 'submitted':submitted})
            
            except Exception as e:
                print(f'ERROR IS{e}')
                return render(request, 'estate/error_page.html', {'e': e}, {e})
        
        else:
                messages.info(request, 'Verify your email to start listing with us')
                return redirect('customer:update-profile', user_id=request.user.id)
    else:
        messages.info(request, ('Join us Now to start'))
        return redirect('login')


#listing properties for rent
def lease_property(request):
    if request.user.is_authenticated:
        
        #user must have an email befre he/she can list with us
        if (request.user.role == 'customer' and request.user.email) or (request.user.role == 'company' or request.user.role == 'agent'):
            
            try:
                submitted= False
                
                if request.method== 'POST':
                    prop_form=LeaseForm(request.POST or None, request.FILES or None) #request.FILES to handle the images 
                    image_form=RentImageFormSet(request.POST or None, request.FILES or None)
                    with transaction.atomic():
                        if prop_form.is_valid() and image_form.is_valid():
                            print(prop_form.errors)
                            landlord= prop_form.save(commit=False)
                            try:
                                company= CompanyInformation.objects.get(user_id= request.user.id)
                                landlord.company_uuid= company.unique_company_id
                                landlord.user_id= request.user.id
                                landlord.time_stamp= timezone.now()
                                landlord.save()
                                image_form.instance=landlord
                                image_form.save()
                            except CompanyInformation.DoesNotExist:
                                landlord.user_id= request.user.id
                                landlord.time_stamp= 0
                                landlord.save()
                                image_form.instance=landlord
                                image_form.save()
                            #making sure form is submitted once
                        return HttpResponseRedirect('?submitted=True')
                    
                else:
                    prop_form= LeaseForm()
                    image_form=RentImageFormSet()
                    if 'submitted' in request.GET:
                        submitted=True
                        
                return render(request, 'estate/lease_property.html', {'form': prop_form,'image_form':image_form, 'submitted':submitted})
            
            except Exception as e:
                print(f'ERROR IS{e}')
                return render(request, 'estate/error_page.html', {'e': e})
            
        else:
            messages.info(request, 'Verify email to start listing with us')
            return redirect('customer:update-profile', user_id=request.user.id)

    else:
        messages.info(request, ('Join us Now to start'))
        return redirect('login')



#list for all properties on sale
def buy_property(request):
    if request.user.is_authenticated:
        
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
            
            
            return render(request, 'estate/buy_property.html', {'buy': on_sale,'nums':nums, 'salefilter':myfilter})
        
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.info(request, ('Join us Now to start'))
        return redirect('login')


#list of all leased property
def rent_property(request):
        if request.user.is_authenticated:
            
            try:
                
                rent_qs=PropertyManagementRent.objects.all().order_by('-listed_date')
                #pagination and listing
                myfilter=PropertyRentFilter(request.GET, queryset=rent_qs)
                rent_qs=myfilter.qs
                p=Paginator(rent_qs, 9)
                page= request.GET.get('page')
                on_lease= p.get_page(page)
                nums= "a" * on_lease.paginator.num_pages
                return render(request, 'estate/rent_property.html', {'nums':nums, 'on_lease': on_lease, 'rentfilter':myfilter})
            
            except Exception as e:
                print(f'ERROR IS{e}')
                return render(request, 'estate/error_page.html', {'e': e})
            
        else:
            messages.info(request, ('Join Estate Web Now!!!'))
            return redirect('login')


#view to update listed property on rent
def update_property_rent(request, property_id):
    if request.user.is_authenticated:
        
        try:
            #gets the particular listing that needs to be updated using the property id
            property=PropertyManagementRent.objects.get(pk= property_id)
            #limiting update property acess to the owner of listing
            if property.user_id == request.user.id:
                prop_form= LeaseForm(request.POST or None,request.FILES or None, instance=property)
                image_form = RentImageFormSet(request.POST or None, request.FILES or None, instance=property)

                if prop_form.is_valid() and image_form.is_valid():
                    prop_form.save()
                    image_form.save()
                    messages.success(request, "Property Updated Successfully")
                    print(property.base_image.url)
                    return redirect('customer:my-listings')
                return render(request, 'estate/update_property.html', {'property': property, 'form': prop_form, 'images': image_form})
            
            else:
                messages.warning(request, 'You do not have access to this page')
                return redirect('customer:user-profile')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.info(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


#view to update listed property on rent
def update_property_sale(request, property_id):
    if request.user.is_authenticated:
        
        try:
            #updating the particular listing that needs to be updated using the property id
            property=PropertyManagementSale.objects.get(pk= property_id)
            
            #limiting update access to owner of listings
            if property.user_id == request.user.id:
                prop_form= SellForm(request.POST or None, request.FILES or None, instance=property)
                image_form = SaleImageFormSet(request.POST or None, request.FILES or None, instance=property)
                
                if prop_form.is_valid() and image_form.is_valid():
                    prop_form.save()
                    image_form.save()
                    messages.success(request, "Property Updated Successfully")
                    return redirect('customer:my-listings')
                return render(request, 'estate/update_property_s.html', {'property': property, 'form': prop_form,'images': image_form})
            
            else:
                messages.warning(request, 'You do not have access to this page')
                return redirect('customer:user-profile')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


#view to delete listings
def delete_property_on_lease(request, property_id):
    if request.user.is_authenticated:
        
        try:
            #deleting using th property id
            property1= PropertyManagementRent.objects.get(pk=property_id)
            
            #protects against other user deleting ones property
            if request.user.id == property1.user_id:
                #what does the actual deleting based on the property_id
                property1.delete()
                messages.success(request, ("Property deleted successfully"))
                return redirect('customer:my-listings')
            
            else:
                messages.warning(request, ('You Arent authorized to delete this property'))
                return redirect('customer:my-listings')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


#view to delete listings
def delete_property_on_sale(request, property_id):
    if request.user.is_authenticated:
        
        try:
            property1= PropertyManagementSale.objects.get(pk=property_id)
            
            #Additional layer of security
            if request.user.id == property1.user_id:
                property1.delete()
                messages.success(request, ("Property deleted successfully"))
                return redirect('customer:my-listings')
            
            else:
                messages.warning(request, ('You Arent authorized to delete this property'))
                return redirect('customer:my-listings')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


#full details of listed property
def view_property_on_sale(request, property_id):
    if request.user.is_authenticated:
        
        try:
            property= PropertyManagementSale.objects.get(pk=property_id)
            property_image=property.images.all()
            email=request.user.email #contact information
            user=User.objects.get(pk=request.user.id)
            #checking if owner of listing is an estate agent
            if property.company_uuid != 'None':
                company_handled=CompanyInformation.objects.get(unique_company_id=property.company_uuid)
            
                try:
                    analytics=company_handled.analytics.get()
                except ObjectDoesNotExist:
                    analytics = CompanyAnalytics.objects.create(
                        company=company_handled,
                        profile_views=0, 
                        property_views_l=0,
                        property_views_s=0,
                        last_month_profile_views=0,
                        last_month_lease_views=0,
                        last_month_sale_views=0,
                    )
                time_since_reset= abs(timezone.now() - property.last_reset_date)
                final_property_time= time_since_reset.days
                if final_property_time > 30:
                    analytics.last_month_sale_views= analytics.property_views_s
                    analytics.property_views_s = 0
                    property.last_reset_date=timezone.now()
                    analytics.save()
                    property.save()
                try:
                    prop_analytics=property.prop_analytics.get(session_id=request.user.id)
                except ObjectDoesNotExist:
                    prop_analytics=PropertyManagementSaleAnalytics.objects.create(
                        on_sale= property,
                        session_id=request.user.id,
                        inquires_check=0
                    )
                    analytics.property_views_s +=1
                    analytics.save()
                company_info=company_handled
                messages.info(request, f'Listing Is handled by {company_handled.company_name}')
                return render(request, 'estate/view_property_s.html', {'property':property,'images':property_image, 
                                                                'email':email, 'user':user, 'company_info':company_info})
            elif property.agent_uuid != 'None':
                agent_handled=Agent_Information.objects.get(user_id=property.user_id)
                agent_info=agent_handled.personal_info
                messages.info(request, f'Listing Is handled by a universal agent')
                return render(request, 'estate/view_property_s.html', {'property':property,'images':property_image, 
                                                                'agent_info':agent_info, 'email':email, 'user':user})
        
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
        
        try:
            email=request.user.email#contact information
            property= PropertyManagementRent.objects.get(pk=property_id)
            property_images= property.images.all()
            user=User.objects.get(pk=request.user.id)
            if property.company_uuid != 'None':
                company_handled=CompanyInformation.objects.get(unique_company_id=property.company_uuid)
                try:
                    analytics=company_handled.analytics.get()
                except ObjectDoesNotExist:
                    analytics = CompanyAnalytics.objects.create(
                        company=company_handled,
                        profile_views=0, 
                        property_views_l=0,
                        property_views_s=0,
                        last_month_profile_views=0,
                        last_month_lease_views=0,
                        last_month_sale_views=0,
                    )
                time_since_reset= abs(timezone.now() - property.last_reset_date)
                final_property_time= time_since_reset.days
                if final_property_time > 30:
                    analytics.last_month_lease_views= analytics.property_views_l
                    analytics.property_views_l = 0
                    property.last_reset_date=timezone.now()
                    analytics.save()
                    property.save()
                try:
                    prop_analytics=property.prop_analytics.get(session_id=request.user.id)
                except ObjectDoesNotExist:
                    prop_analytics=PropertyManagementRentAnalytics.objects.create(
                        on_lease= property,
                        session_id=request.user.id,
                        inquires_check=0
                    )
                    analytics.property_views_l +=1
                    analytics.save()
                company_info=company_handled
                messages.info(request, f'Listing Is handled by {company_handled.company_name}')
                return render(request, 'estate/view_property_r.html', {'property':property,'images':property_images, 
                                                                'email':email, 'user':user, 'company_info':company_info})
            elif property.agent_uuid != 'None':
                agent_handled=Agent_Information.objects.get(user_id=property.user_id)
                agent_info=agent_handled.personal_info
                messages.info(request, f'Listing Is handled by a universal agent')
                return render(request, 'estate/view_property_r.html', {'property':property,'images':property_images, 
                                                                'agent_info':agent_info, 'email':email, 'user':user})
        
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
            
                try:
                    info= Agent_Information.objects.get(user_id=request.user.id) #needed for django template in html side
                    return render(request, 'estate/user_profile.html', {'headline': ns.article_headline, 'info':info})#news headline is passed
                
                except Agent_Information.DoesNotExist:
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
    
    try:
        property_obj = get_object_or_404(PropertyManagementRent, id=property_id)
        lease = get_object_or_404(PropertyManagementRent, id=property_id)
        #What handles the wishlist toggling
        lease.whilist = not lease.whilist
        lease.save()
        wishlist_item, created = WishlistForRent.objects.get_or_create(property=property_obj, user=request.user)
        
        if not created:
            wishlist_item.delete()
            messages.success(request, "Property removed from your wishlist.")
        else:
            messages.success(request, "Property added to your wishlist.")

        return redirect('customer:rent-prop')
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})


#view for toggling the on and off of my wishlist
def toggle_wishlist_buy(request, property_id):
    if not request.user.is_authenticated:
        
        messages.warning(request, "You need to be logged in to access this page.")
        return redirect('landing')
    
    try:
        buy = get_object_or_404(PropertyManagementSale, id=property_id)
        #What handles the wishlist toggling
        buy.whilist = not buy.whilist
        buy.save()
        property_obj = get_object_or_404(PropertyManagementSale, id=property_id)
        wishlist_item, created = WishlistForSale.objects.get_or_create(property=property_obj, user=request.user)
        
        if not created:
            wishlist_item.delete()
            messages.success(request, "Property removed from your wishlist.")
            
        else:
            messages.success(request, "Property added to your wishlist.")
        return redirect('customer:buy-property')  
    
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})


#View listing all the users wishlist
def wishlist(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to be logged in to access this page.")
        return redirect('landing')
    
    try:
        #fetching the related forign key object in a single query
        wishlist_rent = WishlistForRent.objects.filter(user=request.user).select_related('property')
        wishlist_sale = WishlistForSale.objects.filter(user=request.user).select_related('property')

        #Total items in wishlist
        total_saved = wishlist_rent.count() + wishlist_sale.count()

        context = {
            'wishlist_rent': wishlist_rent,
            'wishlist_sale': wishlist_sale,
            'total_saved': total_saved,
        }
        return render(request, 'estate/wishlist.html', context)
    
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})


#view handling update of user profile
def update_profile(request, user_id):
    if request.user.is_authenticated:
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
        
        try:
            messages.info(request, 'Communication Prefrences and privacy will come in future Updates Stayed Tuned😊')
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
        try:
            #getting all that needs to be deleted if a users account was actually deleted
            property1= PropertyManagementRent.objects.filter(user_id=request.user.id)
            property2= PropertyManagementSale.objects.filter(user_id=request.user.id)
            agent_info=Agent_Information.objects.filter(user_id=request.user.id)
            
            
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


#form for estate agents to fill
def estate_agent_form(request):
    if request.user.is_authenticated:
        
        try:
            #checking if one has already fill the form to avoid duplicate data
            if not Agent_Information.objects.get(user_id=request.user.id):
                messages.info(request, 'Set up your Profile to gain customers Trust')
                agent_form = AgentInformationForm(request.POST or None)
                user_form = UserInformationForm(request.POST or None)
                exp_formset = ExperienceFormSet(request.POST or None)
                soc_formset = SocialLinksFormSet(request.POST or None)

                if request.method == 'POST':
                    if agent_form.is_valid() and user_form.is_valid() and exp_formset.is_valid() and soc_formset.is_valid():
                        
                        #performing more than one database operation
                        with transaction.atomic():
                            user_info = user_form.save()
                            agent_info = agent_form.save(commit=False)
                            agent_info.personal_info = user_info
                            agent_info.user_id= request.user.id
                            agent_info.save()
                            exp_formset.instance = agent_info
                            exp_formset.save()
                            soc_formset.instance = agent_info
                            soc_formset.save()
                        messages.success(request, 'Profile Set Successfully')
                        return redirect('customer:user-profile')
                    return render(
                        request,
                        'estate/agent_form.html',
                        {
                            'agent_form': agent_form,
                            'user_form': user_form,
                            'exp_form': exp_formset,
                            'soc_form': soc_formset,
                        },
                    )
                    
            else:
                #if someone has filled the form activate update mode
                messages.info(request, 'Update Work Profile')
                agent_inforation=Agent_Information.objects.get(user_id=request.user.id)
                agent_form = AgentInformationForm(request.POST or None, instance=agent_inforation)
                user_form = UserInformationForm(request.POST or None,instance=agent_inforation.personal_info)
                exp_formset = ExperienceFormSet(request.POST or None, instance=agent_inforation)
                soc_formset = SocialLinksFormSet(request.POST or None, instance=agent_inforation)
                if agent_form.is_valid() and user_form.is_valid() and exp_formset.is_valid() and soc_formset.is_valid():
                    
                    #multiple database operation
                    with transaction.atomic():
                        
                            user_info = user_form.save()
                            agent_info = agent_form.save(commit=False)
                            agent_info.personal_info = user_info
                            agent_info.user_id= request.user.id
                            agent_info.save()
                            exp_formset.instance = agent_info
                            exp_formset.save()
                            soc_formset.instance = agent_info
                            soc_formset.save()
                            messages.success(request, 'Profile Updated successfully')
                            return redirect('customer:user-profile')
                return render(request, 'estate/update_agent_form.html', 
                        {
                            'agent_form': agent_form,
                            'user_form': user_form,
                            'exp_form': exp_formset,
                            'soc_form': soc_formset,
                        }
                )
                
        except Exception as e:
            print(f'ERROR IS {e}')
            return render(request, 'estate/error_page.html', {'e': e}, {e})



    else:
        messages.error(request, 'You must be logged in to access this page')
        return redirect('landing')


#estate aget profile view
def estate_agent_profile(request, agent_id):
    if request.user.is_authenticated:
        try:
            #all the agents information
            agent_info= Agent_Information.objects.get(user_id=agent_id)
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
                    inq_form.agent_id='None'
                    inq_form.property_type='Rent'
                    inq_form.property_name=on_rent.house_type
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
                    inq_form.agent_id='None'
                    inq_form.property_type='Sale'
                    inq_form.property_name=on_sale.house_type
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