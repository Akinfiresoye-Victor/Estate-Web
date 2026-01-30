from django.shortcuts import render, redirect, get_object_or_404
from .models import AgentInformation, SessionId, AgentAnalytics, UniversalAgent, AgentRating
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
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from .quotes import get_random_quote
from django.db.models import Sum, Avg, Count
from core.utils import monthly_change, engagement_rate, reset_button, total_agents_engagement_calculator



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
                elif current_hour >= 12 and current_hour < 16:
                    greeting='Good Afternoon'
                else:
                    greeting='Good Evening'
                    
                quote = get_random_quote()
                tips = quote['tips']
                by = quote['by']
                agent_prop_on_lease=PropertyManagementRent.objects.filter(agent_uuid=agent_data.agent_uuid)
                agent_prop_on_sale=PropertyManagementSale.objects.filter(agent_uuid=agent_data.agent_uuid)
                
                
                leads=LeadInfo.objects.filter(agent_id=agent_data.agent_uuid)
                new_leads= leads.filter(date_created=datetime.today())
                
                
                '''Today's Appointment'''
                
                today_appointments=Appointments.objects.filter(agent_uuid=agent_data.agent_uuid).filter(appointment=datetime.today())
                rating_data = AgentRating.objects.filter(
                    agent_uuid=agent_data.agent_uuid
                ).aggregate(
                    avg_rating=Avg('rating'),
                    total_reviews=Count('id')
                )
                average_rating = rating_data['avg_rating'] or 0.0
                total_reviews = rating_data['total_reviews']
                
                
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
                    'todays_appointment':today_appointments,
                    'avg_rating': average_rating,
                    'total_reviews': total_reviews
                })
        except AgentInformation.DoesNotExist:
            messages.error(request, 'Set up your Profile to access other pages')
            return redirect('agent:agent-form')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})





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

def update_agent_profile(request, agent_uuid):
    """
    Update agent profile with proper formset handling
    """
    # Authentication checks
    if not request.user.is_authenticated:
        messages.info(request, 'You have to be logged in to access this page')
        return redirect('landing')
    
    if request.user.role != 'agent':
        messages.error(request, 'Open an agent account to access this page')
        return redirect('landing')
    
    try:
        # Get the agent information
        agent_information = AgentInformation.objects.get(agent_uuid=agent_uuid)
        
        # Authorization check
        if request.user.id != agent_information.user_id:
            messages.error(request, 'You do not have permission to edit this profile')
            return redirect('agent:agent-settings')
        
        if request.method == 'POST':
            # IMPORTANT: Pass instance for formsets even in POST
            form = AgentInformationForm(
                request.POST, 
                request.FILES, 
                instance=agent_information
            )
            social_form = SocialLinksFormSet(
                request.POST, 
                instance=agent_information
            )
            exp_form = ExperienceFormSet(
                request.POST, 
                instance=agent_information
            )
            
            # Validate all forms
            if form.is_valid() and social_form.is_valid() and exp_form.is_valid():
                try:
                    with transaction.atomic():
                        # Save main form
                        agent = form.save(commit=False)
                        agent.user = request.user
                        agent.user_id = request.user.id
                        agent.save()
                        
                        # Save formsets (they're already linked to agent via instance)
                        social_form.save()
                        exp_form.save()
                        
                        messages.success(request, 'Profile updated successfully!')
                        return redirect('agent:settings')
                        
                except Exception as e:
                    messages.error(request, f'Error saving profile: {str(e)}')
                    print(f'Save error: {e}')
            else:
                # Collect all errors for debugging
                error_messages = []
                
                if form.errors:
                    error_messages.append(f'Form errors: {form.errors}')
                
                if social_form.errors:
                    error_messages.append(f'Social links errors: {social_form.errors}')
                
                if exp_form.errors:
                    error_messages.append(f'Experience errors: {exp_form.errors}')
                
                # Display first error to user
                if error_messages:
                    messages.error(request, 'Please correct the errors in the form')
                    print('\n'.join(error_messages))
        
        else:
            # GET request - initialize forms with instance
            form = AgentInformationForm(instance=agent_information)
            social_form = SocialLinksFormSet(instance=agent_information)
            exp_form = ExperienceFormSet(instance=agent_information)
        
        context = {
            'form': form,
            'social_form': social_form,
            'exp_form': exp_form
        }
        
        return render(request, 'agent/update_agent_form.html', context)
    
    except ObjectDoesNotExist:
        messages.error(request, 'Agent profile not found')
        return redirect('agent:agent-settings')
    
    except Exception as e:
        print(f'Unexpected error: {e}')
        return render(request, 'estate/error_page.html', {'e': e})
        

    


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
    """Display agent profile with reviews"""
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        agent = get_object_or_404(AgentInformation, agent_uuid=agent_uuid)
        
        # Get reviews
        reviews = AgentRating.objects.filter(
            agent_uuid=agent_uuid
        ).select_related('user').order_by('-created_at')[:10]  # Latest 10 reviews
        
        # Calculate rating statistics
        rating_data = AgentRating.objects.filter(
            agent_uuid=agent_uuid
        ).aggregate(
            average=Avg('rating'),
            total=Count('id')
        )
        
        average_rating = rating_data['average'] or 0.0
        total_reviews = rating_data['total'] or 0
        
        # Check if current user has reviewed
        user_has_reviewed = False
        if request.user.is_authenticated:
            user_has_reviewed = AgentRating.objects.filter(
                agent_uuid=agent_uuid,
                user=request.user
            ).exists()
        
        # Get agent's other data (adjust based on your models)
        house_count = agent.properties.count() if hasattr(agent, 'properties') else 0
        lead_count = agent.leads.count() if hasattr(agent, 'leads') else 0
        new_lead_count = agent.leads.filter(status='new').count() if hasattr(agent, 'leads') else 0
        
        context = {
            'agent': agent,
            'name': agent.profile_name if hasattr(agent, 'profile_name') else agent.user.get_full_name(),
            'work_type': agent.work_type if hasattr(agent, 'work_type') else 'Real Estate Agent',
            'email': agent.email if hasattr(agent, 'email') else agent.user.email,
            'phone': agent.phone_number if hasattr(agent, 'phone_number') else '',
            'location': agent.location if hasattr(agent, 'location') else '',
            'house_count': house_count,
            'lead_count': lead_count,
            'new_lead_count': new_lead_count,
            'base_template': base_template,
            
            # Review context
            'reviews': reviews,
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'user_has_reviewed': user_has_reviewed,
        }
        
        return render(request, 'agent/agent_profile.html', context)
        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})










def analytics(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.error(request, "Agent's Only")
        return redirect('landing')
    
    try:
        current_agent = AgentInformation.objects.get(user_id=request.user.id)
        
        analytics_data, created = AgentAnalytics.objects.get_or_create(
            agent=current_agent,
            defaults={
                'profile_views': 0,
                'property_views_l': 0,
                'property_views_s': 0,
                'average_profile_views': 0,
                'average_lease_views': 0,
                'average_sale_views': 0,
                'ratings': 0.0,
                'reviews': 0,
                'competition': 0.0
            }
        )
        
        # Calculate property views for CURRENT agent only
        lease_views = PropertyViews.objects.filter(
            property_type='Rent',
            property_id__in=PropertyManagementRent.objects.filter(
                agent_uuid=current_agent.agent_uuid
            ).values_list('pk', flat=True)
        ).count()
        
        sale_views = PropertyViews.objects.filter(
            property_type='Sale',
            property_id__in=PropertyManagementSale.objects.filter(
                agent_uuid=current_agent.agent_uuid
            ).values_list('pk', flat=True)
        ).count()
        
        # Save the new counts for CURRENT agent
        analytics_data.property_views_l = lease_views
        analytics_data.property_views_s = sale_views
        analytics_data.save()
        
        # Reset monthly tracking if needed
        reset_button(analytics_data, current_agent.agent_uuid, lease_views, sale_views)
        
        # Calculate percentage changes
        lease_views_change = monthly_change(analytics_data.property_views_l, analytics_data.average_lease_views)
        sale_views_change = monthly_change(analytics_data.property_views_s, analytics_data.average_sale_views)
        profile_views_change = monthly_change(analytics_data.profile_views, analytics_data.average_profile_views)
        total_prop_incr_perc = (sale_views_change + lease_views_change) / 2
        
        # ========================================
        # 2. CALCULATE COMPETITION (READ-ONLY)
        # ========================================
        
        # Get ALL agents' analytics in one query (READ ONLY - don't modify!)
        all_analytics = AgentAnalytics.objects.select_related('agent').all()
        
        total_agents_eng = []
        
        for record in all_analytics:
            # Calculate engagement for each agent using EXISTING data
            ag_rent_likes = PropertyManagementRent.objects.filter(
                agent_uuid=record.agent.agent_uuid
            ).aggregate(total=Sum('total_likes'))['total'] or 0
            
            ag_sale_likes = PropertyManagementSale.objects.filter(
                agent_uuid=record.agent.agent_uuid
            ).aggregate(total=Sum('total_likes'))['total'] or 0
            
            ag_total_likes = ag_rent_likes + ag_sale_likes
            ag_rating_score = (record.ratings or 0) * (record.reviews or 0)
            ag_avg_prop_views = record.average_sale_views + record.average_lease_views
            
            # Calculate engagement score
            ag_eng_rate = engagement_rate(
                ag_total_likes,
                ag_avg_prop_views,
                record.average_profile_views,
                ag_rating_score
            )
            
            total_agents_eng.append(ag_eng_rate)
            
            # If this is the current agent, save their score
            if record.agent.id == current_agent.id:
                analytics_data.competition = ag_eng_rate
                analytics_data.save()
        
        # ========================================
        # 3. CALCULATE MARKET POSITION
        # ========================================
        current_agent_score = analytics_data.competition
        
        if total_agents_eng and len(total_agents_eng) > 1:
            sorted_eng = sorted(total_agents_eng, reverse=True)
            agents_above = sum(1 for score in sorted_eng if score > current_agent_score)
            market_position = (agents_above / len(sorted_eng)) * 100
            
            if market_position <= 1:
                top_performer = "Top 1%"
            elif market_position <= 5:
                top_performer = "Top 5%"
            elif market_position <= 10:
                top_performer = "Top 10%"
            elif market_position <= 25:
                top_performer = "Top 25%"
            else:
                top_performer = f"Top {int(market_position)}%"
        else:
            top_performer = "New Agent"
            market_position = 100
        
        # Calculate competition metrics
        total_eng_sum = sum(total_agents_eng)
        avg_prop_views = analytics_data.average_lease_views + analytics_data.average_sale_views
        
        calculated_engagement = total_agents_engagement_calculator(
            total_eng_sum,
            current_agent_score,
            current_agent.agent_uuid,
            avg_prop_views
        )
        
        competition_pct = calculated_engagement[0]
        inq_conv_rate = calculated_engagement[1]
        
        # ========================================
        # 4. GET TOP PROPERTIES
        # ========================================
        agent_props_rent = PropertyManagementRent.objects.filter(agent_uuid=current_agent.agent_uuid)
        agent_props_sale = PropertyManagementSale.objects.filter(agent_uuid=current_agent.agent_uuid)
        
        all_properties = list(agent_props_rent) + list(agent_props_sale)
        all_properties.sort(key=lambda x: x.total_likes, reverse=True)
        top_properties = all_properties[:4]
        
        # Get views for top 4 properties
        view_list = []
        for prop in top_properties:
            cnt = PropertyViews.objects.filter(
                property_id=prop.pk,
                property_type=prop.property_type
            ).count()
            view_list.append(cnt)
        
        likes_views = zip(top_properties, view_list)
        
        # ========================================
        # 5. RETURN CONTEXT
        # ========================================
        context = {
            'profile_views': analytics_data.profile_views,
            'listing_views': analytics_data.property_views_l + analytics_data.property_views_s,
            'lease_views': analytics_data.property_views_l,
            'sale_views': analytics_data.property_views_s,
            'profile_incr_perc': profile_views_change,
            'lease_incr_perc': lease_views_change,
            'sale_incr_perc': sale_views_change,
            'total_prop_incr_perc': total_prop_incr_perc,
            'competition': market_position,
            'inq_rate': inq_conv_rate,
            'ranking': likes_views
        }
        
        return render(request, 'agent/agent_analytics.html', context)
        
    except AgentInformation.DoesNotExist:
        messages.error(request, 'Agent profile not found.')
        return redirect('landing')
        
    except Exception as e:
        print(f"Error in analytics view: {e}")  # Debug logging
        return render(request, 'estate/error_page.html', {'e': str(e)})

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


@require_POST
def agent_update_lead_status(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'log in to access this page')
        return redirect('landing')
    if request.user.role != 'agent':
        messages.info(request, 'Access Denied')
        return redirect('landing')
    try:
        try:
            agent = AgentInformation.objects.get(user_id=request.user.id)
            lead = LeadInfo.objects.get(pk=lead_id)
            
            new_status = request.POST.get('new_status')
            if not new_status:
                messages.error(request, 'Status Missing')
                return redirect('agent:leads')
            
            lead.status = new_status
            lead.date_updated = timezone.now()
            lead.save()
            
            messages.success(request, 'Status Updated Successfully')
            return redirect('agent:lead-detail', lead_id=lead_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Lead Not found')
            return redirect('agent:leads')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})


@require_POST
def agent_update_lead_stage(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain access')
        return redirect('landing')
    if request.user.role != 'agent':
        messages.info(request, 'Access Denied')
        return redirect('landing')
    try:
        try:
            agent = AgentInformation.objects.get(user_id=request.user.id)
            lead = LeadInfo.objects.get(pk=lead_id)
            
            new_stage = request.POST.get('new_stage')
            if not new_stage:
                messages.error(request, 'Stage Missing')
                return redirect('agent:leads')
            
            lead.stages = new_stage
            lead.date_updated = timezone.now()
            lead.save()
            
            messages.success(request, 'Stage Updated Successfully')
            return redirect('agent:lead-detail', lead_id=lead_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Lead Not found')
            return redirect('agent:leads')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def settings(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.error(request, "Agent's Only")
        return redirect('landing')
    try:
        agent= AgentInformation.objects.get(user_id=request.user.id)
        context={
            'agent':agent
        }
        return render(request, 'agent/settings.html', context)
    except ObjectDoesNotExist:
        messages.error(request, 'Error Agent Info Missing')
        return redirect('landing')
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




# TODO try to add the mini scraper 

def job_listings(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.info(request, 'Agents Only')
        return redirect('lnding')
    
    try:
        return render(request, 'agent/job_listings.html')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})



def delete_agent(request, agent_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.info(request, 'Agents Only')
        return redirect('landing')
    
    try:
        agent_data=AgentInformation.objects.get(agent_uuid=agent_uuid)
        if agent_data.user_id != request.user.id:
            messages.warning(request, 'Unauthorized Access')
            return redirect('landing')
        user_id=User.objects.get(pk=request.user.id)
        leads= LeadInfo.objects.filter(agent_id=agent_data.agent_uuid)
        appointments= Appointments.objects.filter(agent_uuid=agent_data.agent_uuid)
        property_views=PropertyViews.objects.filter(uuid=agent_data.agent_uuid)
        sale_properties= PropertyManagementSale.objects.filter(agent_uuid=agent_data.agent_uuid)
        lease_properties= PropertyManagementRent.objects.filter(agent_uuid=agent_data.agent_uuid)
        try:
            lease_properties.delete()
            sale_properties.delete()
            property_views.delete()
            appointments.delete()
            leads.delete()
            user_id.delete()
        except:
            messages.error(request, 'An error Occured.....')
            return redirect('landing')
        messages.success(request, 'User Deleted Successfully')
        return redirect('landing')
    except ObjectDoesNotExist:
        messages.error(request, 'Tell Us the error')
        return render(request, 'estate/error_page.html', {'e':'Object Doesnt Exist'})
    except Exception as e:
        messages.error(request, 'Tell us the error')
        return render(request, 'estate/error_page.html', {'e':e})