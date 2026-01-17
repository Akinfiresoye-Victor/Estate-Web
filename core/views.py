from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.http import HttpResponseRedirect
from django.db import transaction
from companies.models import CompanyInformation
from . import news_scrape as ns
from admin_panel.views import admin
from agents.models import AgentInformation
from estate.models import LeadInfo
from django.core.exceptions import ObjectDoesNotExist


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
                        with transaction.atomic():
                            landlord= prop_form.save(commit=False)
                            category = prop_form.cleaned_data.get('property_category')
                            # Clear the non-selected fields
                            if category == 'Residential':
                                landlord.commercial = ''
                                landlord.lands = ''
                            elif category == 'Commercial':
                                landlord.residential = ''
                                landlord.lands = ''
                            elif category == 'Land':
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
                        return render(request, 'estate/error_page.html', {'e': prop_form.errors})
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
                    if prop_form.is_valid() and image_form.is_valid():
                        with transaction.atomic():
                            landlord= prop_form.save(commit=False)
                            category = prop_form.cleaned_data.get('property_category')
                            
                            # Clear the non-selected fields
                            if category == 'Residential':
                                landlord.commercial = ''
                                landlord.lands = ''
                            elif category == 'Commercial':
                                landlord.residential = ''
                                landlord.lands = ''
                            elif category == 'Land':
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
                        return render(request, 'estate/error_page.html', {'e': prop_form.errors})
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
                    return redirect('listings')
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
                    return redirect('listings')
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
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        #deleting using th property id
        property1= PropertyManagementRent.objects.get(pk=property_id)
        #protects against other user deleting ones property
        if request.user.id == property1.user_id:
            #what does the actual deleting based on the property_id
            property1.delete()
            messages.success(request, ("Property deleted successfully"))
            return redirect('listings')
        
        else:
            messages.error(request, ('Access Denied'))
            return redirect('listings')
        
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})

#view to delete listings
def delete_property_on_sale(request, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        property1= PropertyManagementSale.objects.get(pk=property_id)
        
        #Additional layer of security
        if request.user.id == property1.user_id:
            property1.delete()
            messages.success(request, ("Property deleted successfully"))
            return redirect('listings')
        
        else:
            messages.warning(request, ('Access Denied'))
            return redirect('listings')
        
    except Exception as e:
        print(f'ERROR IS{e}')
        return render(request, 'estate/error_page.html', {'e': e})
# FIXME Delete Problem if a property is deleted everything must be deleted alongside with it 
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
            property1= PropertyManagementRent.objects.filter(user_id=model).order_by('-listed_date')
            property2= PropertyManagementSale.objects.filter(user_id=model).order_by('-listed_date')
            return render(request, 'core/my_listings.html', {'property1':property1, 'property2':property2, 'base_template':base_template})
        except Exception as e:
            print(f'ERROR IS{e}')
            return render(request, 'estate/error_page.html', {'e': e})
        
    else:
        messages.warning(request, ('You need to be logged in to accesss this page'))
        return redirect('landing')


def partner_with_us(request):
    return render(request, 'core/partner.html')



#TODO Cross check all authentication side to affect loss of data 

def appointment_detail(request,lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Log In required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.info(request, 'Access Denied')
        return redirect('landing')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        if request.user.role == 'company':
            company=CompanyInformation.objects.get(user_id=request.user.id)
            appointment= Appointments.objects.filter(company_uuid=company.unique_company_id).get(pk=lead_id)
        else:
            agent=AgentInformation.objects.get(user_id=request.user.id)
            appointment= Appointments.objects.filter(agent_uuid=agent.agent_uuid).get(pk=lead_id)
        try:
            lead=LeadInfo.objects.get(lead_id=appointment.lead_uuid)
            return render(request, 'core/appointment_detail.html', {'appointment': appointment, 'lead_data': lead, 'base_template':base_template})
        except ObjectDoesNotExist:
            return render(request, 'core/appointment_detail.html', {'appointment': appointment, 'base_template':base_template})
        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})

def add_schedule(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Log In required')
        return redirect('login')
    
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        if request.method == 'POST':
            form = AppointmentForm(request.POST)
            
            if form.is_valid():
                appointment = form.save(commit=False)
                
                if request.user.role == 'company':
                    company=CompanyInformation.objects.get(user_id=request.user.id)
                    appointment.company_uuid = str(company.unique_company_id)
                elif request.user.role == 'agent':
                    agent=AgentInformation.objects.get(user_id=request.user.id)
                    appointment.agent_uuid = str(agent.agent_uuid)
                
                # Handle property selection if provided
                property_id = request.POST.get('property_id')
                property_type = request.POST.get('property_type')
                
                if property_id:
                    appointment.property_id = property_id
                if property_type:
                    appointment.property_type = property_type
                
                # Handle lead/customer selection if provided
                lead_uuid = request.POST.get('lead_uuid')
                if lead_uuid:
                    appointment.lead_uuid = lead_uuid
                
                appointment.save()
                
                messages.success(request, 'Appointment scheduled successfully!')
                return redirect('appointment') 
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = AppointmentForm()
        
        context = {
            'form': form,
            'base_template':base_template
            # Add any additional context like leads, properties, etc.
            # 'leads': Lead.objects.filter(company_uuid=request.user.uuid),
            # 'properties': Property.objects.filter(company_uuid=request.user.uuid),
        }
        
        return render(request, 'core/add_schedule.html', context)
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'estate/error_page.html', {'e': e})


def appointment(request):
    if not request.user.is_authenticated:
        messages.info(request, "Login Required")
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        
        '''Client Appointment'''
        #user in question
        try:
            company= CompanyInformation.objects.get(user_id=request.user.id)
            total_appointment= Appointments.objects.filter(company_uuid=company.unique_company_id)
            return render(request, 'core/appointment.html', {'appointments': total_appointment, 'base_template':base_template})
        except ObjectDoesNotExist:
            agent= AgentInformation.objects.get(user_id=request.user.id)
            total_appointment= Appointments.objects.filter(agent_uuid=agent.agent_uuid)
            return render(request, 'core/appointment.html', {'appointments': total_appointment,'base_template':base_template ,'agent_name':agent.profile_name})
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def estate_blog(request):
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        return render(request, 'core/estate_blog.html', {'base_template': base_template})
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'estate/error_page.html', {'e': e})


def manaage_listings(request):
    if not request.user.is_authenticated:
        messages.info(request, 'login required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.warning(request, 'Access Restricted')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        if request.user.role == 'company':
            user_type=CompanyInformation.objects.get(user_id=request.user.id)
            user_id=user_type.unique_company_id
            property_on_lease=PropertyManagementRent.objects.filter(company_uuid=user_id)
            property_on_sale=PropertyManagementSale.objects.filter(company_uuid=user_id)
            role='company'
        else:
            user_type=AgentInformation.objects.get(user_id=request.user.id)
            user_id=user_type.agent_uuid
            property_on_lease=PropertyManagementRent.objects.filter(agent_uuid=user_id)
            property_on_sale=PropertyManagementSale.objects.filter(agent_uuid=user_id)
            role='agent'
        
        return render(request, 'core/listings.html', {'on_lease':property_on_lease,'role':role,
                                                        'on_sale':property_on_sale, 'base_template':base_template})
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})


def edit_appointment(request, appointment_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Log In required')
        return redirect('login')
    
    if request.user.role == 'customer':
        messages.info(request, 'Access Denied')
        return redirect('landing')
    
    try:
        user_role = request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template = 'estate/base.html'
        
        # Get the appointment based on user role
        if request.user.role == 'company':
            company = CompanyInformation.objects.get(user_id=request.user.id)
            appointment = Appointments.objects.filter(
                company_uuid=company.unique_company_id
            ).get(pk=appointment_id)
        else:
            agent = AgentInformation.objects.get(user_id=request.user.id)
            appointment = Appointments.objects.filter(
                agent_uuid=agent.agent_uuid
            ).get(pk=appointment_id)
        #TODO Implement security measures in situations where update is critical
        # Get lead information if exists
        lead = None
        try:
            if appointment.lead_uuid:
                lead = LeadInfo.objects.get(lead_id=appointment.lead_uuid)
        except ObjectDoesNotExist:
            pass
        
        # Handle POST request (form submission)
        if request.method == 'POST':
            try:
                # Update appointment fields
                appointment.appointment = request.POST.get('appointment_date')
                appointment.note = request.POST.get('note', 'No Note Provided')
                appointment.appointment_type = request.POST.get('appointment_type')
                
                # Update property fields if provided
                property_id = request.POST.get('property_id')
                if property_id:
                    appointment.property_id = int(property_id)
                
                property_type = request.POST.get('property_type')
                if property_type:
                    appointment.property_type = property_type
                
                appointment.save()
                
                messages.success(request, 'Appointment updated successfully!')
                return redirect('view-schedule', lead_id=appointment_id)
                
            except Exception as e:
                messages.error(request, f'Error updating appointment: {str(e)}')
        
        # Get appointment types for the dropdown
        appointment_types = dict(APPOINTMENT_TYPE)
        
        context = {
            'appointment': appointment,
            'lead_data': lead,
            'base_template': base_template,
            'appointment_types': appointment_types,
        }
        
        return render(request, 'core/edit_appointment.html', context)
        
    except Appointments.DoesNotExist:
        messages.error(request, 'Appointment not found')
        return redirect('appointments_list')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def view_client(request, appointment_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    user_role = request.user.role
    if user_role == 'company':
        base_template = 'company/base.html'
    elif user_role == 'agent':
        base_template = 'agent/base.html'
    else:
        base_template = 'estate/base.html'
    try:
        try:
            company=CompanyInformation.objects.get(user_id= request.user.id)
            leads=LeadInfo.objects.filter(company_uuid=company.unique_company_id)
        except:
            agent= AgentInformation.objects.get(user_id=request.user.id)
            leads= LeadInfo.objects.filter(agent_id=agent.agent_uuid)
        return render(request, 'core/lead_list.html', {'leads': leads, 'base_template': base_template, 'appointment_id':appointment_id})
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})


def add_client(request, lead_uuid, appointment_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        appointment_data= Appointments.objects.get(pk=appointment_id)
        lead_data= LeadInfo.objects.get(lead_id=lead_uuid)
        appointment_data.lead_uuid= lead_data.lead_id
        appointment_data.save()
        messages.success(request, 'Client Added')
        return redirect('view-schedule', appointment_id)
    except Exception as e:
        return render(request, 'estate/error_page', {'e':e})
    
    
def delete_client(request, appointment_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        appointment=Appointments.objects.get(pk=appointment_id)
        if request.user.role == 'company':
            try:
                company= CompanyInformation.objects.get(user_id=request.user.id)
                if appointment.company_uuid == company.unique_company_id:
                    appointment.lead_uuid = None
                    appointment.save()
                    messages.success(request, 'Client Info Removed')
                    return redirect('view-schedule', appointment_id)
                else:
                    messages.error(request, 'Access Denied')
                    return redirect('landing')
            except ObjectDoesNotExist:
                messages.error(request, 'An error occured')
                return redirect('landing')
        elif request.user.role == 'agent':
            try:
                agent=AgentInformation.objects.get(user_id=request.user.id)
                if appointment.agent_uuid == agent.agent_uuid:
                    appointment.lead_uuid = None
                    appointment.save()
                    messages.success(request, 'Client Info Removed')
                    return redirect('view-schedule', appointment_id)
                else:
                    messages.error(request, 'Access Denied')
                    return redirect('landing')
            except ObjectDoesNotExist:
                messages.error(request, 'An error occured')
                return redirect('landing')
        else:
            messages.error(request, 'Access Denied')
            return redirect('landing')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})