from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.contrib import messages
from members.forms import UpdateUserForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from . import news_scrape as ns
from django.core.paginator import Paginator
from .filters import *
from django.db import transaction
from datetime import datetime, date
from django.contrib.auth.models import User
from django.utils import timezone


ADMIN='PY.PRO'


'''Landing Page Views'''
def welcome_page(request):
    if request.user.is_authenticated:
        messages.success(request, 'Welcome Back')
        return redirect('user-profile')
    else:
        return render(request, 'estate/welcome_page.html')


def about_us(request):
    return render(request, 'estate/about_me.html')


'''News Views'''
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
            return redirect('user-profile')
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


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
                    return redirect('feedback')
            else:
                form = FeedbackForm()
                if 'submitted' in request.GET:
                    submitted = True
            return render(request, 'estate/feedback.html', {'form': form, 'submitted': submitted})
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {e})
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#for admins only
def view_feedbacks(request):
    if request.user.id == 1:
        feedbacks=Feedback.objects.all()
        return render(request,'estate/views.html', {'feedback': feedbacks})

#for admins only
def delete_feedback(request, feedback_id):
    if request.user.is_authenticated:
        #getting the property_id which will be used to handle the deletion
        feedback= Feedback.objects.get(pk=feedback_id)
        #keeps another user from deleting a users data 
        if request.user.id == 1:
            #what does the actual deleting based on the property_id
            feedback.delete()
            messages.success(request, ("Feedback deleted successfully"))
            return redirect('view-feedbacks')
        else:
            messages.error(request, ('You Arent authorized to delete this feedback'))
            return redirect('my-listings')
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')



'''Property Management'''

#listing properties for sale
def sell_property(request):
    if request.user.is_authenticated:
        
        #user must have an email before he/she can list a property
        if request.user.email:
            
            try:
                
                submitted= False

                if request.method== 'POST':
                    prop_form=SellForm(request.POST or None, request.FILES or None)
                    image_form=SaleImageFormSet(request.POST or None, request.FILES or None)
                    if prop_form.is_valid() and image_form.is_valid():
                        
                        with transaction.atomic():
                            landlord= prop_form.save(commit=False)
                            landlord.user_id= request.user.id
                            landlord.save()
                            image_form.instance= landlord
                            image_form.save()
                        return HttpResponseRedirect('/sell_property?submitted=True')
                    
                else:
                    prop_form= SellForm()
                    image_form=SaleImageFormSet()
                    
                    if 'submitted' in request.GET:
                        submitted=True
                
                return render(request, 'estate/sell_property.html', {'form': prop_form,'image_form':image_form, 'submitted':submitted})
            
            except Exception as e:
                print(f'ERROR IS{e}')
                return render(request, 'estate/error_page.html', {e})
        
        else:
                messages.info(request, 'Verify your email to start listing with us')
                return redirect('update-profile', user_id=request.user.id)
    else:
        messages.info(request, ('Join us Now to start'))
        return redirect('login')


#listing properties for rent
def lease_property(request):
    if request.user.is_authenticated:
        
        #user must have an email befre he/she can list with us
        if request.user.email:
            
            try:
                submitted= False
                
                if request.method== 'POST':
                    prop_form=LeaseForm(request.POST or None, request.FILES or None) #request.FILES to handle the images 
                    image_form=RentImageFormSet(request.POST or None, request.FILES or None)
                    with transaction.atomic():
                        if prop_form.is_valid() and image_form.is_valid():
                            print(prop_form.errors)
                            landlord= prop_form.save(commit=False)
                            landlord.user_id= request.user.id
                            landlord.save()
                            image_form.instance=landlord
                            image_form.save()
                            #making sure form is submitted once
                        return HttpResponseRedirect('/lease_property?submitted=True')
                    
                else:
                    prop_form= LeaseForm()
                    image_form=RentImageFormSet()
                    if 'submitted' in request.GET:
                        submitted=True
                        
                return render(request, 'estate/lease_property.html', {'form': prop_form,'image_form':image_form, 'submitted':submitted})
            
            except Exception as e:
                print(f'ERROR IS{e}')
                return render(request, 'estate/error_page.html')
            
        else:
            messages.info(request, 'Verify email to start listing with us')
            return redirect('update-profile', user_id=request.user.id)

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
            return render(request, 'estate/buy_property.html', {'buy': on_sale,'nums':nums, 'salefilter':myfilter })
        
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
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
                return render(request, 'estate/error_page.html')
            
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
                    return redirect('my-listings')
                return render(request, 'estate/update_property.html', {'property': property, 'form': prop_form, 'images': image_form})
            
            else:
                messages.warning(request, 'You do not have access to this page')
                return redirect('user-profile')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.info(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


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
                    return redirect('my-listings')
                return render(request, 'estate/update_property_s.html', {'property': property, 'form': prop_form,'images': image_form})
            
            else:
                messages.warning(request, 'You do not have access to this page')
                return redirect('user-profile')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


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
                return redirect('my-listings')
            
            else:
                messages.warning(request, ('You Arent authorized to delete this property'))
                return redirect('my-listings')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#view to delete listings
def delete_property_on_sale(request, property_id):
    if request.user.is_authenticated:
        
        try:
            property1= PropertyManagementSale.objects.get(pk=property_id)
            
            #Additional layer of security
            if request.user.id == property1.user_id:
                property1.delete()
                messages.success(request, ("Property deleted successfully"))
                return redirect('my-listings')
            
            else:
                messages.warning(request, ('You Arent authorized to delete this property'))
                return redirect('my-listings')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#full details of listed property
def view_property_on_sale(request, property_id):
    if request.user.is_authenticated:
        
        try:
            property= PropertyManagementSale.objects.get(pk=property_id)
            property_image=property.images.all()
            email=request.user.email #contact information
            
            try:
                #checking if owner of listing is an estate agent
                info=Agent_Information.objects.get(user_id=property.user_id)
                
                if info:
                    info=info.personal_info
                messages.info(request, 'Listing Is handled by an agent')
                return render(request, 'estate/view_property_s.html', {'property':property,'images':property_image, 'info':info, 'email':email})
            
            #if the owner of listing is an home owner
            except Agent_Information.DoesNotExist:
                messages.info(request, 'Image Problem will be fixed soon stay alert for future updates')
                messages.info(request, 'Listing Is handled by the home owner')
                return render(request, 'estate/view_property_s.html', {'property':property, 'email':email})
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#Full details of listing
def view_property_on_lease(request, property_id):
    if request.user.is_authenticated:
        
        try:
            email=request.user.email#contact information
            property= PropertyManagementRent.objects.get(pk=property_id)
            property_images= property.images.all()
            try:
                #checking of property lister is an agent
                info=Agent_Information.objects.get(user_id=property.user_id)
                
                if info:
                    info=info.personal_info
                messages.info(request, 'Image Problem will be fixed soon stay alert for future updates')
                messages.info(request, 'Listing Is handled by an agent')
                return render(request, 'estate/view_property_r.html', {'property':property,'images':property_images, 'info':info, 'email':email})
            
            #if not
            except Agent_Information.DoesNotExist:
                messages.info(request, 'Image Problem will be fixed soon stay alert for future updates')
                messages.info(request, 'Listing Is handled by the home owner')
                return render(request, 'estate/view_property_r.html', {'property':property, 'email':email})
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')





'''User Handling Views'''

#view handling the users profile settings
def user_profile(request):
    try:
        if request.user.is_authenticated:
            
                try:
                    info= Agent_Information.objects.get(user_id=request.user.id) #needed for django template in html side
                    return render(request, 'estate/user_profile.html', {'headline': ns.article_headline, 'info':info})#news headline is passed
                
                except Agent_Information.DoesNotExist:
                        return render(request, 'estate/user_profile.html', {'headline': ns.article_headline})
                    
        else:
            messages.warning(request, ('You need to be logged in to accesss this page'))
            return redirect('welcome-page')
        
    except Exception as e:
        print(e)


#view handling users listings
def listed_properties(request):
    if request.user.is_authenticated:
        
        try:
            
            model= request.user.id
            #filtering the listings using both the users id and the properties id(Hacked my way through this🤡)
            if request.user.username == ADMIN:
                property1= PropertyManagementRent.objects.order_by('-listed_date')
                property2= PropertyManagementSale.objects.order_by('-listed_date')
                return render(request, 'estate/my_listings.html', {'property1':property1, 'property2':property2})
            else:
                property1= PropertyManagementRent.objects.filter(user_id=model).order_by('-listed_date')
                property2= PropertyManagementSale.objects.filter(user_id=model).order_by('-listed_date')
                return render(request, 'estate/my_listings.html', {'property1':property1, 'property2':property2})
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#view for toggling the on and off of my wishlist
def toggle_wishlist_rent(request, property_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to be logged in to access this page.")
        return redirect('welcome-page')
    
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

        return redirect('rent-prop')
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html')


#view for toggling the on and off of my wishlist
def toggle_wishlist_buy(request, property_id):
    if not request.user.is_authenticated:
        
        messages.warning(request, "You need to be logged in to access this page.")
        return redirect('welcome-page')
    
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
        return redirect('buy-property')  
    
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html')


#View listing all the users wishlist
def wishlist(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to be logged in to access this page.")
        return redirect('welcome-page')
    
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
        return render(request, 'estate/error_page.html')


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
                    return redirect('user-profile')
                
                else:
                    messages.error(request, 'check If you made any errors')
                return render(request, 'estate/update_profile.html', {'profile': profile, 'form': form})
            
            else:
                messages.warning(request, 'Youre not allowed to access this page')
                return redirect('user-profile')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


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
                    return redirect('password-success')
                
                else:
                    messages.error(request, 'There was an error changing your password.... please try again..')
                    return redirect('change-password')
                
            else:
                form= PasswordChangeForm(request.user)
                return render(request, 'estate/change_passw.html', {'form': form})
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.info(request, 'You have to be logged in to access this page')
        return redirect('welcome-page')


#success page after password change
def change_password_success(request):
    if request.user.is_authenticated:
        
        try:
            return render(request, 'estate/succ_pass.html')
        
        except Exception as e:
            print(f'ERROR IS {e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, 'You need to be logged in to access this page')
        return redirect('welcome-page')


#Users Settings
def profile_settings(request):
    if request.user.is_authenticated:
        
        try:
            messages.info(request, 'Communication Prefrences and privacy will come in future Updates Stayed Tuned😊')
            return render(request, 'estate/settings.html', {})
        
        except Exception as e:
            print(f'ERROR IS {e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.warning(request, 'You need to be logged in to access this page')
        return redirect('welcome-page')



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
                return redirect('user-profile')
            messages.success(request, 'Account has been deleted Successfully')
            return redirect('welcome-page')
        
        except Exception as e:
            print(f'ERROR IS {e}')
            return render(request, 'estate/error_page.html')
        
    else:
        messages.info(request, 'You have to be logged in to access this page')
        return redirect('welcome-page')


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
                        return redirect('user-profile')
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
                            return redirect('user-profile')
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
            return render(request, 'estate/error_page.html', {e})



    else:
        messages.error(request, 'You must be logged in to access this page')
        return redirect('welcome-page')


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
            return render(request, 'estate/error_page.html')
        
    else:
        messages.info('You have to be logged in to access this page')
        return redirect('welcome-page')


'''Analytics For admin'''

#Total Listings and sign uo
def admin_dashboard(request):
    if request.user.username == ADMIN:
        
        '''Property Tracking'''
        on_lease=PropertyManagementRent.objects.all()
        on_sale= PropertyManagementSale.objects.all()
        
        # Listings Calculation
        x_initial=PropertyManagementRent.objects.count() #where x is property on lease
        y_initial=PropertyManagementSale.objects.count() #where y is property on lease

        prop_calc=property_tracking(on_lease, on_sale, x_initial, y_initial)
        user_track=user_tracking()
        
        #properties calc
        total_listings=prop_calc[0]
        total_perc=prop_calc[1]
        percentage_rent= prop_calc[2]
        percentage_sale=prop_calc[3]
        final_rent_time= prop_calc[4]
        final_sale_time=prop_calc[5]
        final_update_time= prop_calc[6]
        todays_property=prop_calc[7]
        
        '''User Tranking'''
        user_count=user_track[0]
        user_increase_percentage= user_track[1]
        daily_active_users= user_track[2]
        final_time=user_track[3]

        
        context = {'users':user_count,
                    'users_inc_perc': user_increase_percentage,
                    'dau':daily_active_users,
                    'user_reg_time':final_time,
                    'on_lease_count': x_initial,
                    'on_sale_count':y_initial,
                    'total_listings': total_listings,
                    'rent_perc': percentage_rent,
                    'sale_perc': percentage_sale,
                    'total_perc': total_perc,
                    'rent_time':final_rent_time,
                    'sale_time':final_sale_time,
                    'final_update_time': final_update_time,
                    'today_property':todays_property}
        return render(request, 'estate/admin_dashboard.html',context)
        


def property_tracking(on_lease, on_sale, x_initial, y_initial):
        
        x=0
        x_prev=0
        y=0
        y_prev=0
        
        '''Property count '''
        for prop in on_lease:
            if prop.listed_date.date() == date.today():
                x+=1
            else:
                x_prev += 1
        
        for prop in on_sale:
            if prop.listed_date.date() == date.today():
                y+=1
            else:
                y_prev += 1
        initial_time_listed_r=PropertyManagementRent.objects.order_by('-listed_date').first()
        initial_time_listed_s=PropertyManagementSale.objects.order_by('-listed_date').first()
        
        "Recent history"
        raw_rent_time=timezone.now() - initial_time_listed_r.listed_date
        formatted_rent_time=abs(raw_rent_time.total_seconds() / 60)
        final_rent_time=time_formatting(formatted_rent_time)
        
        raw_sale_time=abs(timezone.now() - initial_time_listed_s.listed_date)
        formatted_sale_time=raw_sale_time.total_seconds() / 60
        final_sale_time=time_formatting(formatted_sale_time)
        
        
        raw_rent_update_time= timezone.now() - initial_time_listed_r.last_updated
        formatted_rent_update_time=abs(raw_rent_update_time.total_seconds() / 60)
        final_rent_update_time=time_formatting(formatted_rent_update_time)
        
        raw_sale_update_time= timezone.now() - initial_time_listed_s.last_updated
        formatted_sale_update_time=abs(raw_sale_update_time.total_seconds() / 60)
        
        if formatted_sale_update_time > formatted_rent_update_time:
            formatted_update_time=formatted_sale_update_time
        elif formatted_sale_update_time < formatted_rent_update_time:
            formatted_update_time=formatted_rent_update_time
        else:
            formatted_update_time= (formatted_rent_update_time + formatted_sale_update_time) /2
        final_update_time= time_formatting(formatted_update_time)
        
        percentage_sale= (y/y_prev) * 100
        percentage_rent= (x/x_prev) * 100   
        
        total_perc= percentage_rent + percentage_sale
        total_listings= x_initial + y_initial
        
        property_listed_today=x + y
        
        calculated_percentages_list= [total_listings, total_perc, percentage_rent, percentage_sale, final_rent_time,
                                    final_sale_time, final_update_time, property_listed_today]
        return calculated_percentages_list

def user_tracking():
    user=User.objects.all()
    user_count=User.objects.count()
    
    
    users_today=0
    prev_users=0
    for users in user:
        if users.date_joined.date() == date.today():
            users_today += 1
        else:
            prev_users += 1
            
            
    daily_active_users=0
    for users in user:
        if users.last_login.date() == date.today():
            daily_active_users += 1
    
    user_increase_percentage= (users_today / prev_users) * 100
    
    
    
    # "%Y-%m-%d %H:%M:%S"
    lates_user=User.objects.order_by('-date_joined').first()
    user_reg_time= timezone.now() - lates_user.date_joined
    formatted_time=user_reg_time.total_seconds()/60
    final_time=time_formatting(formatted_time)
    user_tracking_list= [user_count,user_increase_percentage, daily_active_users, final_time]
    return user_tracking_list



def time_formatting(formatted_time):
    if formatted_time >= 60 and formatted_time <= 1439:
        formatted_time/=60
        if formatted_time == 1:
            final_time=f'{int(formatted_time)} Hours ago'
        else:
            final_time=f'{int(formatted_time)} Hours ago'
    elif formatted_time >= 1440:
        formatted_time/=1400
        if formatted_time == 1:
            final_time=f'{int(formatted_time)} Day Ago'
        else:
            final_time=f'{int(formatted_time)} Days Ago'
        
    else:
        if formatted_time <= 1:
            final_time=f'{int(formatted_time)} minute ago'
        else:
            final_time=f'{int(formatted_time)} minutes ago'
    return final_time