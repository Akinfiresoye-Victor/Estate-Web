from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.http import HttpResponseRedirect
from django.db import transaction
from companies.models import CompanyInformation
from . import news_scrape as ns
from admin_panel.views import admin
from agents.models import AgentInformation


# Create your views here.
def landing_page(request):
    if not request.user.is_authenticated:
        return render(request, 'core/landing.html')
    else:
        if request.user.role == 'company':
            return redirect('company:dashboard')
        elif request.user.role == 'agent':
            return redirect('agent:dashboard')
        elif request.user.role == 'customer':
            return redirect('customer:user-profile')
        else:
            return render(request, 'core/landing.html')

def about_page(request):
    return render(request, 'core/about.html')


'''Users Feedbacks'''
def feedbacks(request):
    if request.user.is_authenticated:
        try:
            submitted = False
            user_role=request.user.role
            if user_role == 'company':
                base_template = 'company/base.html'
            elif user_role == 'agent':
                base_template = 'agent/base.html'
            else:
                base_template='estate/base.html'
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
            return render(request, 'core/feedback.html', {'form': form, 'submitted': submitted, 'base_template':base_template})
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
                user_role=request.user.role
                if user_role == 'company':
                    base_template = 'company/base.html'
                elif user_role == 'agent':
                    base_template = 'agent/base.html'
                else:
                    base_template='estate/base.html'
                submitted= False

                if request.method== 'POST':
                    prop_form=SellForm(request.POST or None, request.FILES or None)
                    image_form=SaleImageFormSet(request.POST or None, request.FILES or None)
                    if prop_form.is_valid() and image_form.is_valid():
                        print('valid')
                        with transaction.atomic():
                            landlord= prop_form.save(commit=False)
                            category = prop_form.cleaned_data.get('property_category')
                            print(category)
                            # Clear the non-selected fields
                            if category == 'Residential':
                                landlord.commercial = ''
                                landlord.lands = ''
                            elif category == 'Commercial':
                                landlord.residential = ''
                                landlord.lands = ''
                            elif category == 'Plot/Land':
                                landlord.residential = ''
                                landlord.commercial = ''
                            try:
                                company= CompanyInformation.objects.get(user_id= request.user.id)
                                landlord.company_uuid= company.unique_company_id
                                landlord.user_id= request.user.id
                                landlord.time_stamp=timezone.now()
                                landlord.save()
                                image_form.instance=landlord
                                image_form.save()
                            except CompanyInformation.DoesNotExist:
                                agent=AgentInformation.objects.get(user_id=request.user.id)
                                landlord.agent_uuid=str(agent.agent_uuid)
                                if agent.company_uuid:
                                    landlord.company_uuid = agent.company_uuid
                                landlord.user_id= request.user.id
                                landlord.time_stamp= timezone.now()
                                landlord.save()
                                image_form.instance=landlord
                                image_form.save()
                        return HttpResponseRedirect('?submitted=True')
                    else:
                        print('not valid')
                        print(prop_form.errors)
                        category = prop_form.cleaned_data.get('property_category')
                        print(category)
                else:
                    prop_form= SellForm()
                    image_form=SaleImageFormSet()
                    
                    if 'submitted' in request.GET:
                        submitted=True
                
                return render(request, 'core/sell_property.html', {'form': prop_form,'image_form':image_form, 'submitted':submitted, 'base_template':base_template})
            
            except Exception as e:
                print(f'ERROR IS{e}')
                return render(request, 'estate/error_page.html', {'e': e})
        
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
                user_role=request.user.role
                if user_role == 'company':
                    base_template = 'company/base.html'
                elif user_role == 'agent':
                    base_template = 'agent/base.html'
                else:
                    base_template='estate/base.html'
                if request.method== 'POST':
                    prop_form=LeaseForm(request.POST or None, request.FILES or None) #request.FILES to handle the images 
                    image_form=RentImageFormSet(request.POST or None, request.FILES or None)
                    with transaction.atomic():
                        if prop_form.is_valid() and image_form.is_valid():
                            landlord= prop_form.save(commit=False)
                            category = prop_form.cleaned_data.get('property_category')
                            
                            # Clear the non-selected fields
                            if category == 'Residential':
                                landlord.commercial = ''
                                landlord.lands = ''
                            elif category == 'Commercial':
                                landlord.residential = ''
                                landlord.lands = ''
                            elif category == 'Plot/Land':
                                landlord.residential = ''
                                landlord.commercial = ''
                            try:
                                company= CompanyInformation.objects.get(user_id= request.user.id)
                                landlord.company_uuid= company.unique_company_id
                                landlord.user_id= request.user.id
                                landlord.time_stamp= timezone.now()
                                landlord.save()
                                image_form.instance=landlord
                                image_form.save()
                            except CompanyInformation.DoesNotExist:
                                agent= AgentInformation.objects.get(user_id=request.user.id)
                                landlord.agent_uuid= agent.agent_uuid
                                if agent.company_uuid != None:
                                    landlord.company_uuid= agent.company_uuid
                                landlord.user_id= request.user.id
                                landlord.time_stamp= timezone.now()
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
                        
                return render(request, 'core/lease_property.html', {'form': prop_form,'image_form':image_form, 'submitted':submitted, 'base_template':base_template})
            
            except Exception as e:
                print(f'ERROR IS {e}')
                return render(request, 'estate/error_page.html', {'e': e})
            
        else:
            messages.info(request, 'Verify email to start listing with us')
            return redirect('customer:update-profile', user_id=request.user.id)

    else:
        messages.info(request, ('Join us Now to start'))
        return redirect('login')


'''News Blog Automation'''
def articles(request):
    if request.user.is_authenticated:
        try:
            user_role=request.user.role
            if user_role == 'company':
                base_template = 'company/base.html'
            elif user_role == 'agent':
                base_template = 'agent/base.html'
            else:
                base_template='estate/base.html'
            #news headlines
            headlines= ns.bs.find('div', class_="blog-item-title")
            headlines=headlines.text
            #estate article content
            article= ns.bs.find('div', class_="blog-item-content e-content")
            article=article.text
            full_article= "https://www.nigeriahousingmarket.com/"
            return render(request,'core/article.html', {'headline':headlines,
                                                        'article':article,
                                                        "full_article":full_article,
                                                        'base_template':base_template})
        except:
            messages.error(request, ns.error)
            return redirect('customer:user-profile')
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')





#view to update listed property on rent
def update_property_rent(request, property_id):
    if request.user.is_authenticated:
        
        try:
            #gets the particular listing that needs to be updated using the property id
            property=PropertyManagementRent.objects.get(pk= property_id)
            user_role=request.user.role
            if user_role == 'company':
                base_template = 'company/base.html'
            elif user_role == 'agent':
                base_template = 'agent/base.html'
            else:
                base_template='estate/base.html'
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
                return render(request, 'core/update_property.html', {'property': property, 'form': prop_form, 'images': image_form, 'base_template':base_template})
            
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
            user_role=request.user.role
            if user_role == 'company':
                base_template = 'company/base.html'
            elif user_role == 'agent':
                base_template = 'agent/base.html'
            else:
                base_template='estate/base.html'
            #limiting update access to owner of listings
            if property.user_id == request.user.id:
                prop_form= SellForm(request.POST or None, request.FILES or None, instance=property)
                image_form = SaleImageFormSet(request.POST or None, request.FILES or None, instance=property)
                
                if prop_form.is_valid() and image_form.is_valid():
                    prop_form.save()
                    image_form.save()
                    messages.success(request, "Property Updated Successfully")
                    return redirect('my-listings')
                return render(request, 'core/update_property_s.html', {'property': property, 'form': prop_form,'images': image_form, 'base_template':base_template})
            
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
                return redirect('my-listings')
            
            else:
                messages.warning(request, ('You Arent authorized to delete this property'))
                return redirect('my-listings')
            
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
                return redirect('my-listings')
            
            else:
                messages.warning(request, ('You Arent authorized to delete this property'))
                return redirect('my-listings')
            
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


#view handling users listings
def listed_properties(request):
    if request.user.is_authenticated:
        try:
            user_role=request.user.role
            if user_role == 'company':
                base_template = 'company/base.html'
            elif user_role == 'agent':
                base_template = 'agent/base.html'
            else:
                base_template='estate/base.html'
            model= request.user.id
            #filtering the listings using both the users id and the properties id(Hacked my way through this🤡)
            if request.user.username == admin:
                property1= PropertyManagementRent.objects.order_by('-listed_date')
                property2= PropertyManagementSale.objects.order_by('-listed_date')
                return render(request, 'core/my_listings.html', {'property1':property1, 'property2':property2})
            else:
                property1= PropertyManagementRent.objects.filter(user_id=model).order_by('-listed_date')
                property2= PropertyManagementSale.objects.filter(user_id=model).order_by('-listed_date')
                return render(request, 'core/my_listings.html', {'property1':property1, 'property2':property2, 'base_template':base_template})
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')
