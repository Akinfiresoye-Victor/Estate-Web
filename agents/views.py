from django.shortcuts import render, redirect
from .models import AgentInformation, SessionId, AgentAnalytics
from django.contrib import messages
from .forms import AgentInformationForm, SocialLinksFormSet, ExperienceFormSet
from django.db import transaction
from members.models import User
from django.http import HttpResponseRedirect
from django.utils import timezone
from core.models import PropertyManagementRent, PropertyManagementSale, PropertyViews, Appointments
from estate.models import LeadInfo
from datetime import datetime
from datetime import date
from companies.views import property_views_count





# Create your views here.
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('landing')
    if not request.user.role == 'agent':
        return redirect('landing')
    try:
        try:
            if AgentInformation.objects.get(user_id=request.user.id):
                agent_data= AgentInformation.objects.get(user_id=request.user.id)
                agent_name=agent_data.profile_name
                agent_profession=agent_data.work_type
                agent_email=agent_data.email
                agent_phone=agent_data.phone_number
                agent_location=agent_data.location
                first_name=agent_name.split()
                first_name=first_name[0]
                raw_time=timezone.localtime(timezone.now())
                current_hour=raw_time.hour
                if current_hour >= 0 and current_hour < 12:
                    greeting='Good Morning'
                    tips='Success in Real estate starts when you are worthy of it'
                    by='Michael Ferrara'
                elif current_hour >= 12 and current_hour < 16:
                    greeting='Good Afternoon'
                    tips="To be consistent in real estate, you must always and consistently put your clients'best Intrest First"
                    by= 'Anthony Hitt'
                else:
                    greeting='Good Evening'
                    tips='Real Estate is the purest form of Entrepreneurship'
                    by='brian Bufini'
                agent_prop_on_lease=PropertyManagementRent.objects.filter(agent_uuid=agent_data.agent_uuid)
                agent_prop_on_sale=PropertyManagementSale.objects.filter(agent_uuid=agent_data.agent_uuid)
                
                
                leads=LeadInfo.objects.filter(agent_id=agent_data.agent_uuid)
                new_leads= leads.filter(date_created=datetime.today())
                
                
                '''Today's Appointment'''
                
                today_appointments=Appointments.objects.filter(agent_uuid=agent_data.agent_uuid).filter(appointment=datetime.today())
                
                
                
                return render(request, 'agent/dashboard.html', {
                    'agent_info':agent_data,
                    'name':agent_name,
                    'work_type': agent_profession,
                    'email': agent_email,
                    'phone': agent_phone,
                    'location': agent_location,
                    'first_name': first_name,
                    'greeting': greeting,
                    'tips': tips,
                    'by': by,
                    'house_count': agent_prop_on_lease.count() + agent_prop_on_sale.count(),
                    'lead_count': leads.count(),
                    'new_lead_count': new_leads.count(),
                    'todays_appointment':today_appointments
                })
        except AgentInformation.DoesNotExist:
            messages.error(request, 'Set up your Profile to access other pages')
            return redirect('agent:agent-form')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})



from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db import transaction
from .models import AgentInformation, UniversalAgent
from .forms import AgentInformationForm, ExperienceFormSet, SocialLinksFormSet

def agent_form(request):
    # Check authentication
    if not request.user.is_authenticated:
        messages.info(request, 'You must be logged in to access this page')
        return redirect('landing')
    
    # Check if user is an agent
    if request.user.role != 'agent':
        messages.error(request, 'Account must be an Agent account to access this page')
        return redirect('landing')
    
    try:
        # Check if agent already has a profile
        if AgentInformation.objects.filter(user_id=request.user.id).exists():
            messages.info(request, 'Form has been filled. Go into edit mode to edit details')
            return redirect('agent:dashboard')
        
        submitted = False
        
        if request.method == 'POST':
            # Initialize forms with POST data
            form = AgentInformationForm(request.POST, request.FILES)
            exp_link = ExperienceFormSet(request.POST, prefix='exp')
            soc_form = SocialLinksFormSet(request.POST, prefix='social')
            
            # Validate all forms
            form_valid = form.is_valid()
            exp_valid = exp_link.is_valid()
            soc_valid = soc_form.is_valid()
            
            # Debug: Print errors if any
            if not form_valid:
                print("Main form errors:", form.errors)
                messages.error(request, f'Main form errors: {form.errors}')
            
            if not exp_valid:
                print("Experience formset errors:", exp_link.errors)
                messages.error(request, f'Experience errors: {exp_link.errors}')
            
            if not soc_valid:
                print("Social formset errors:", soc_form.errors)
                messages.error(request, f'Social links errors: {soc_form.errors}')
            
            # If all forms are valid, save them
            if form_valid and exp_valid and soc_valid:
                try:
                    with transaction.atomic():
                        # Save the main agent form
                        agent = form.save(commit=False)
                        agent.user_id = request.user.id
                        agent.users = request.user
                        
                        # Handle universal_agent checkbox
                        agent.universal_agent = request.POST.get('universal_agent') == 'on'
                        
                        agent.save()
                        print(f"Agent saved with ID: {agent.id}")
                        
                        # Save experience formset
                        experiences = exp_link.save(commit=False)
                        for exp in experiences:
                            exp.agent = agent
                            exp.save()
                        
                        # Handle deleted experiences
                        for exp in exp_link.deleted_objects:
                            exp.delete()
                        
                        print(f"Saved {len(experiences)} experiences")
                        
                        # Save social links formset
                        socials = soc_form.save(commit=False)
                        for social in socials:
                            social.agent = agent
                            social.save()
                        
                        # Handle deleted social links
                        for social in soc_form.deleted_objects:
                            social.delete()
                        
                        print(f"Saved {len(socials)} social links")
                        
                        # Handle Universal Agent data if checkbox was checked
                        if agent.universal_agent:
                            years_exp = request.POST.get('years_experience', '0-1')
                            is_agency = request.POST.get('agency') == 'on'
                            agency_name = request.POST.get('agency_name', 'Not With Agency')
                            
                            UniversalAgent.objects.create(
                                agent=agent,
                                years_experience=years_exp,
                                agency=is_agency,
                                agency_name=agency_name if is_agency else 'Not With Agency'
                            )
                            print("Universal agent data saved")
                        
                        messages.success(request, 'Profile created successfully!')
                        return HttpResponseRedirect(f"{request.path}?submitted=True")
                        
                except Exception as e:
                    print(f"Error saving agent data: {str(e)}")
                    messages.error(request, f'Error saving data: {str(e)}')
                    # Forms will be re-rendered with the POST data below
        
        else:
            # GET request - initialize empty forms
            form = AgentInformationForm()
            exp_link = ExperienceFormSet(prefix='exp')
            soc_form = SocialLinksFormSet(prefix='social')
            
            # Check if we're showing the success page
            if 'submitted' in request.GET:
                submitted = True
        
        return render(request, 'agent/agent_form.html', {
            'form': form,
            'social': soc_form,
            'exp_form': exp_link,
            'submitted': submitted
        })
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'estate/error_page.html', {'e': e})

def update_agent_profile(request, agent_id):
    if not request.user.is_authenticated:
        messages.info(request, 'You have to be logged in to access this page')
        return redirect('landing')
    if request.user.role != 'agent':
        messages.error(request, 'Open an agent account to access this page')
        return redirect('landing')
    try:
        agent_information=AgentInformation.objects.get(pk=agent_id)
        if request.user.id == agent_information.user_id:
            if request.method == 'POST':
                form= AgentInformationForm(request.POST or None, request.FILES)
                social_form=SocialLinksFormSet(request.POST or None)
                exp_form=ExperienceFormSet(request.POST or None)
                if form.is_valid() and social_form.is_valid() and exp_form.is_valid():
                    with transaction.atomic():
                        agent=form.save(commit=False)
                        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})
        
    
    


def lead_management(request):
    if not request.user.is_authenticated:
        messages.info(request, "Login Required")
        return redirect('login')
    if request.user.role != 'agent':
        messages.error(request, "Agent's Only")
        return redirect('landing')
    try:
        agent=AgentInformation.objects.get(user_id=request.user.id)
        leads=LeadInfo.objects.filter(agent_id=agent.agent_uuid)
        new_leads=leads.filter(date_created=date.today()).count()
        qualified_count=leads.filter(status='Qualified').count()
        closed_count=leads.filter(stages='Closed/Won').count()
        
        context={
            'leads':leads,
            'lead_count': leads.count(),
            'new_leads': new_leads,
            'closed_count':closed_count,
            'qualified_count': qualified_count
        }
        return render(request, 'agent/agent_leads.html', context)
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})




def agent_profile(request, agent_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('landing')
    if not request.user.role == 'customer':
        messages.error(request, 'Customer Access Only')
        return redirect('landing')
    
    try:
        agent=AgentInformation.objects.get(agent_uuid=agent_uuid)
        try:
            profile=agent.analytics.get()
        except:
            analytics= AgentAnalytics.objects.create(
                agent=agent,
                profile_views=0,
                ratings=0.0,
                reviews=0
            )
        try:
            session= agent.session_id.get(session_id=request.user.id)
        except:
            session= SessionId.objects.create(
                agent=agent,
                session_id=request.user.id,
                inquires_check=0
            )
            view_count= agent.analytics.get()
            view_count.profile_views+=1
            view_count.save()

        return render(request, 'estate/agent_profile.html', {'agent':agent})
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e', e})



def analytics(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.error(request, "Agent's Only")
        return redirect('landing')
    try:
        agent=AgentInformation.objects.get(user_id= request.user.id)
        agent_lease_properties= PropertyManagementRent.objects.filter(agent_uuid=agent.agent_uuid)
        agent_sales_properties= PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid)
        lease_views_list=[]
        sale_views_list=[]
        
        for prop_id in agent_lease_properties:
            view=property_views_count("Rent", prop_id.pk)
            lease_views_list.append(view)
        for prop_id in agent_sales_properties:
            view=property_views_count("Sale", prop_id.pk)
            sale_views_list.append(view)
        listing_views= sum(lease_views_list) + sum(sale_views_list)
        
        try:
            profile=agent.analytics.get()
        except:
            analytics= AgentAnalytics.objects.create(
                agent=agent,
                profile_views=0,
                ratings=0.0,
                reviews=0
            )
        profile_views= profile.profile_views
        
        total_properties= list(agent_lease_properties) + list(agent_sales_properties)
        total_properties.sort(key=lambda x: x.total_likes, reverse=True)
        total_properties=total_properties[:4]
        view_list=[]
        for prop in total_properties:
            prop_views= PropertyViews.objects.filter(property_type=prop.property_type, property_id=prop.pk).count()
            view_list.append(prop_views)
        likes_views=zip(total_properties, view_list)
        
        
        context={
            "listing_views": listing_views,
            "profile_views": profile_views,
            "sale_views": sum(sale_views_list),
            "lease_views": sum(lease_views_list),
            "ranking": likes_views
        }
        
        return render(request, 'agent/agent_analytics.html', context)
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})




def lead_detail(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return render('login')
    if request.user.role != 'agent':
        messages.error(request, "Agent's Only")
        return redirect('landing')
    try:
        agent=AgentInformation.objects.get(user_id=request.user.id)
        lead=LeadInfo.objects.get(lead_id=lead_id)
        if lead.property_type == 'Sale':
            property_intrested=PropertyManagementSale.objects.get(pk=lead.property_intrested)
        else:
            property_intrested=PropertyManagementRent.objects.get(pk=lead.property_intrested)
        return render(request, 'agent/agent_lead_detail.html', {'lead':lead, 'property':property_intrested})
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})


def settings(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.error(request, "Agent's Only")
        return redirect('landing')
    try:
        return render(request, 'agent/settings.html')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})

def delete_lead(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        agent= AgentInformation.objects.get(user_id=request.user.id)
        lead_to_delete=LeadInfo.objects.get(lead_id=lead_id)
        if agent.agent_uuid == lead_to_delete.agent_id:
            lead_to_delete.delete()
            messages.success(request, "Lead Deleted")
            return redirect('agent:leads')
        else:
            messages.error(request, "Access Denied")
            return redirect('landing')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})





#TODO Perform proper error handling even in places you think error cant occur






