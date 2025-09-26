'''Handles Main Functionality of the Website'''

from django.shortcuts import render, redirect, get_object_or_404
from .models import PropertyManagementSale, PropertyManagementRent
from .forms import LeaseForm, SellForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from members.forms import UpdateUserForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash




#Basic Welcome page for users/guests
def welcome_page(request):
    if request.user.is_authenticated:
        messages.success(request, 'Welcome Back')
        return redirect('user-profile')
    else:
        return render(request, 'estate/welcome_page.html')



'''Property Management Function'''
#Function/View which manages the uploading of properties for sale
def sell_property(request):
    if request.user.is_authenticated:
        submitted= False
        #if the form is submitted do 👇
        if request.method== 'POST':
            form=SellForm(request.POST, request.FILES) #request.FILES helps deals with the picture management
            if form.is_valid():
                landlord= form.save(commit=False)
                landlord.user_id= request.user.id
                form.save()
                return HttpResponseRedirect('/sell_property?submitted=True')#setting the form to true so we dont submit the form twice
        #else just display the form and input required data
        else:
            form= SellForm
            if 'submitted' in request.GET:
                submitted=True
        return render(request, 'estate/sell_property.html', {'form': form, 'submitted':submitted})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#Function/View that manages the uploading of properties for Rent
def lease_property(request):
    if request.user.is_authenticated:
        submitted= False
        if request.method== 'POST':
            form=LeaseForm(request.POST, request.FILES) #request.FILES to handle the images 
            if form.is_valid():
                landlord= form.save(commit=False)
                landlord.user_id= request.user.id
                form.save()
                return HttpResponseRedirect('/lease_property?submitted=True')
        else:
            form= LeaseForm
            if 'submitted' in request.GET:
                submitted=True
        return render(request, 'estate/lease_property.html', {'form': form, 'submitted':submitted})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#Function/View that queries and brings out all the property being leased
def rent_property(request):
    if request.user.is_authenticated:
        #The line that does the actual querying and its organized by the date listed
        leased_property_list= PropertyManagementRent.objects.order_by('-listed_date').all()
        return render(request, 'estate/rent_property.html', {'leased': leased_property_list})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#Function/View that queries and brings out all the property on sale
def buy_property(request):
    if request.user.is_authenticated:
        #The line that does the actual querying and its organized by the date listed from the latest to the oldest 
        propery_sale_list=PropertyManagementSale.objects.order_by('-listed_date').all()
        return render(request, 'estate/buy_property.html', {'buy': propery_sale_list})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View/Function that handles the updating of property already available for rent
def update_property_rent(request, property_id):
    if request.user.is_authenticated:
        #gets the particular listing that needs to be updated using their id
        property=PropertyManagementRent.objects.get(pk= property_id)
        #instance=property then fills the form based on previous data
        form= LeaseForm(request.POST or None,request.FILES or None, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, "Property Updated Successfully")
            return redirect('my-listings')
        return render(request, 'estate/update_property.html', {'property': property, 'form': form})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View/Function that handles the updating of property already available for sale
def update_property_sale(request, property_id):
    if request.user.is_authenticated:
        #gets the particular listing that needs to be updated using their id
        property=PropertyManagementSale.objects.get(pk= property_id)
        #instance=property then fills the form based on previous data
        form= SellForm(request.POST or None, request.FILES or None, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, "Property Updated Successfully")
            return redirect('my-listings')
        return render(request, 'estate/update_property_s.html', {'property': property, 'form': form})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View/Function that deletes unwanted lisings from a users listings
def delete_property_on_lease(request, property_id):
    if request.user.is_authenticated:
        #getting the property_id which will be used to handle the deletion
        property1= PropertyManagementRent.objects.get(pk=property_id)
        #keeps another user from deleting a users data 
        if request.user.id == property1.user_id:
            #what does the actual deleting based on the property_id
            property1.delete()
            messages.success(request, ("Property deleted successfully"))
            return redirect('my-listings')
        else:
            messages.error(request, ('You Arent authorized to delete this property'))
            return redirect('my-listings')
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View/Function that deletes a property on sale using the property id
def delete_property_on_sale(request, property_id):
    if request.user.is_authenticated:
        property1= PropertyManagementSale.objects.get(pk=property_id)
        #Additional layer of security
        if request.user.id == property1.user_id:
            property1.delete()
            messages.success(request, ("Property deleted successfully"))
            return redirect('my-listings')
        else:
            messages.success(request, ('You Arent authorized to delete this property'))
            return redirect('my-listings')
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#Views/Functions that pulls out all details of a property on sale
def view_property_on_sale(request, property_id):
    if request.user.is_authenticated:
        #actual line that does the heavy lifting
        property= PropertyManagementSale.objects.get(pk=property_id)
        return render(request, 'estate/view_property_s.html', {'property':property})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#Views/Functions that pulls out all details of a property on lease
def view_property_on_lease(request, property_id):
    if request.user.is_authenticated:
        #actual line that does the heavy lifting
        property= PropertyManagementRent.objects.get(pk=property_id)
        return render(request, 'estate/view_property_r.html', {'property':property})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View/Function that queries the datatbase containing the properties on lease and ordering them from the lowest price to the highest price
def best_deals_on_lease(request):
    if request.user.is_authenticated:
        property_on_lease= PropertyManagementRent.objects.order_by('price_range').all()
        return render(request, 'estate/best_deals_r.html', {'property': property_on_lease})
    else:
        return redirect('welcome-page')


#View/Function that queries the datatbase containing the properties on sale and ordering them from the lowest price to the highest price
def best_deals_on_sale(request):
    if request.user.is_authenticated:
        property_on_sale= PropertyManagementSale.objects.order_by('price').all()
        return render(request, 'estate/best_deals_s.html', {'property': property_on_sale})
    else:
        return redirect('welcome-page')




'''User Experience Views'''
#view handling the users profile settings
def user_profile(request):
    if request.user.is_authenticated:
        return render(request, 'estate/user_profile.html', {})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View That shows Properties the users listed 
def listed_properties(request):
    if request.user.is_authenticated:
        model1= request.user.id
        model2= request.user.id
        #filtering the listings using both the users id and the properties id 
        property1= PropertyManagementRent.objects.filter(user_id=model1)
        property2= PropertyManagementSale.objects.filter(user_id=model2)
        return render(request, 'estate/my_listings.html', {'property1':property1, 'property2':property2})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View/Function that does the adding of a particular property(Properties Lease) to ones favourite
def toggle_wishlist_rent(request, property_id):
    if request.user.is_authenticated:
        lease = get_object_or_404(PropertyManagementRent, id=property_id)
        #What handles the wishlist toggling
        lease.whilist = not lease.whilist
        lease.save()
        return redirect('rent-prop')
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View/Function that does the adding of a particular property(Properties on Sale) to ones favourite
def toggle_wishlist_buy(request, property_id):
    if request.user.is_authenticated:
        buy=get_object_or_404(PropertyManagementSale, id=property_id)
        #What handles the wishlist toggling
        buy.whilist= not buy.whilist
        buy.save()
        return redirect('buy-property')
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')    


#View/Function That shows all property added to favourites
def wishlist(request):
    if request.user.is_authenticated:
        #this 2 lines get all the objects the heavy lifting is done on the html side(wishlist.html)
        wishlist_rent=PropertyManagementRent.objects.all()
        wishlist_sale=PropertyManagementSale.objects.all()
        return render(request, 'estate/wishlist.html', {'wishlist_rent':wishlist_rent, 'wishlist_sale': wishlist_sale})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View/Function that handles the updating of a users profile
def update_profile(request, user_id):
    if request.user.is_authenticated:
        #The Users data is being pulled out from the database
        profile= User.objects.get(pk=user_id)
        #instance is used to fill the form with former data of the users
        form= UpdateUserForm(request.POST or None, request.FILES or None, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user-profile')
        return render(request, 'estate/update_profile.html', {'profile': profile, 'form': form})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')


#View Or function that uses django PasswordChangeForm to change the users password using old password to set the new password
def change_password(request):
    if request.user.is_authenticated:
        #if the form has been submtted it would check if it met the requirements (.valid) and then save it 
        if request.method == 'POST':
            form= PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                new_pass=form.save()
                #the new password set is then encrypted and saved 
                update_session_auth_hash(request, new_pass)
                messages.success(request, 'Password has been Changed successfully')
                return redirect('password-success')
            else:
                messages.error(request, 'There was an error changing your password.... please try again..')
                return redirect('change-password')
        else:
            form= PasswordChangeForm(request.user)
            return render(request, 'estate/change_passw.html', {'form': form})


#Just a basic view to handle the url pointing to where the site will go after the password has been changed
def change_password_success(request):
    return render(request, 'estate/succ_pass.html')


#Users Settings(More feautures will be added in future updates)
def settings(request):
    messages.success(request, 'Communication Prefrences and privacy will come in future Updates Stayed Tuned😊')
    return render(request, 'estate/settings.html', {})


#View/Function that deletes a users account from the User datatbase and all the properties related to the user so it basically clears all the users datat from the site
def delete_account(request):
    if request.user.is_authenticated:
        #getting all that needs to be deleted if a users account was actually deleted
        property1= PropertyManagementRent.objects.filter(user_id=request.user.id)
        property2= PropertyManagementSale.objects.filter(user_id=request.user.id)
        user_id=User.objects.get(pk=request.user.id)
        #A try block to et any error while deleting the account if not delete account
        try:
            property1.delete()
            property2.delete()
            user_id.delete()
        except Exception as e:
            messages.success(request, 'There was an error, Try again later.....')
            print(e)
            return redirect('user-profile')
        messages.success(request, 'Account has been deleted Successfully')
        return redirect('welcome-page')



'''Search Functionality'''
#View that handles the search functionality of the website
def search_property(request):
    if request.user.is_authenticated:
        #The searched functionality is set empty as default
        searched=''
        #If searched it would then filter all the items in both rent and sale datatbase and brings out their result in respect to properties title
        if request.method=='POST':
            #the item searched for is then passed to get the data from both datatbse
            searched= request.POST['searched']
            properties1=PropertyManagementRent.objects.filter(summary__contains=searched)
            properties2=PropertyManagementSale.objects.filter(summary__contains=searched)
            return render(request, 'estate/search.html', {'searched':searched, 'properties':properties1, 'properties1':properties2})
        else:
            return render(request, 'estate/search.html', {'searched':searched})
    else:
        messages.success(request, ('You need to be logged in to accesss this page'))
        return redirect('welcome-page')