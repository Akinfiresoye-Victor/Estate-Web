from django.shortcuts import render, redirect
from .models import AgentInformation
from django.contrib import messages
from .forms import AgentInformationForm, SocialLinksFormSet, ExperienceFormSet
from django.db import transaction
from members.models import User
from django.http import HttpResponseRedirect
from django.utils import timezone
from core.models import PropertyManagementRent, PropertyManagementSale
from estate.models import LeadInfo
from datetime import datetime
from datetime import date





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
                    'new_lead_count': new_leads.count()
                })
        except AgentInformation.DoesNotExist:
            messages.error(request, 'Set up your Profile to access other pages')
            return redirect('agent:agent-form')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})



def agent_form(request):
    if not request.user.is_authenticated:
        messages.info(request, 'You must be logged in to access this page ')
        return redirect('landing')
    if not request.user.role == 'agent':
        messages.info(request, 'Account must be an Agent account to access this page')
        return redirect('landing')
    
    try:
        # Check if agent already has a profile
        try:
            existing_agent = AgentInformation.objects.get(user_id=request.user.id)
            messages.info(request, 'Form has been filled go into edit mode to edit details')
            return redirect('agent:dashboard')
        except AgentInformation.DoesNotExist:
            messages.info(request, 'Complete Form To gain full access')
        
        submitted = False
        
        if request.method == 'POST':
            
            form = AgentInformationForm(request.POST, request.FILES)
            
            if not form.is_valid():
                print("Form errors:", form.errors)
                messages.error(request, f'Form errors: {form.errors}')
            
            if form.is_valid():
                with transaction.atomic():
                    # Save the main agent form first
                    agent = form.save(commit=False)
                    agent.user_id = request.user.id
                    agent.save()
                    
                    # Now save the formsets with the agent instance
                    exp_link = ExperienceFormSet(request.POST, instance=agent)
                    soc_form = SocialLinksFormSet(request.POST, instance=agent)
                    
                    # DEBUG: Check formset errors
                    if not exp_link.is_valid():
                        print("Experience formset errors:", exp_link.errors)
                    if not soc_form.is_valid():
                        print("Social formset errors:", soc_form.errors)
                    
                    if exp_link.is_valid() and soc_form.is_valid():
                        exp_link.save()
                        soc_form.save()
                        print("Formsets saved successfully")
                        
                        # Handle Universal Agent data if checkbox is checked
                        if request.POST.get('universal_agent'):
                            from .models import UniversalAgent
                            UniversalAgent.objects.create(
                                agent=agent,
                                years_experience=request.POST.get('years_experience', '0-1'),
                                agency=request.POST.get('agency') == 'on',
                                agency_name=request.POST.get('agency_name', 'Not With Agency')
                            )
                            print("Universal agent data saved")
                        
                        messages.success(request, 'Profile created successfully!')
                        return HttpResponseRedirect('?submitted=True')
                    else:
                        # If formsets are invalid, delete the agent
                        agent.delete()
                        messages.error(request, 'Please check the experience and social links sections.')
                        exp_link = ExperienceFormSet(request.POST)
                        soc_form = SocialLinksFormSet(request.POST)
            else:
                exp_link = ExperienceFormSet(request.POST)
                soc_form = SocialLinksFormSet(request.POST)
        else:
            form = AgentInformationForm()
            exp_link = ExperienceFormSet()
            soc_form = SocialLinksFormSet()
            if 'submitted' in request.GET:
                submitted = True
        
        return render(request, 'agent/agent_form.html', {
            'form': form,
            'social': soc_form,
            'exp_form': exp_link,
            'submitted': submitted
        })
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'estate/error_page.html', {'e': e})

def update_agent_profile(request, agent_id):
    if not request.user.is_authenticated:
        messages.info(request, 'You have to be logged in to access this page')
        return redirect('landing')
    if request.user.role != 'agent':
        messages.info(request, 'Open an agent account to access this page')
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
        messages.info(request, "Agent's Only")
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
        messages.info(request, 'Customer Access Only')
        return redirect('landing')
    
    try:
        agent=AgentInformation.objects.get(agent_uuid=agent_uuid)
        return render(request, 'estate/agent_profile.html', {'agent':agent})
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e', e})



def analytics(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.info(request, "Agent's Only")
        return redirect('landing')
    try:
        return render(request, 'agent/agent_analytics.html')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})


#FIXME Work all those back buttons to avoid confusion