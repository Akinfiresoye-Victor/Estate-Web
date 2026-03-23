from django.shortcuts import render, redirect, get_object_or_404
from .models import AgentInformation, SessionId, AgentAnalytics, AgentRating
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
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from companies.models import JobPost,CompanyInformation,InviteLink, CompanyActivityLog, Employees
from django.urls import reverse


# Create your views here.
def calculate_agent_profile_strength(has_picture, has_listing, has_phone):
    """
    Lives outside the view — defined once, not recreated on every request.
    """
    score = 0
    if has_picture: score += 25
    if has_listing: score += 25
    if has_phone:   score += 50
    return score


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('landing')
    if request.user.role != 'agent':
        return redirect('landing')

    try:
        agent_data = AgentInformation.objects.get(user_id=request.user.id)

        # ── Name and greeting ─────────────────────────────────────────────────
        agent_name = f"{agent_data.first_name} {agent_data.last_name}"
        first_name = agent_data.first_name

        raw_time     = timezone.localtime(timezone.now())
        current_hour = raw_time.hour

        if current_hour < 12:
            greeting = 'Good Morning'
        elif current_hour < 16:
            greeting = 'Good Afternoon'
        else:
            greeting = 'Good Evening'

        quote = get_random_quote()

        # ── Property IDs — fetched once, reused for counts ───────────────────
        # Using .exists() and .count() on the same queryset hits DB twice.
        # Fetching IDs once lets us do both with no extra queries.
        rent_ids = set(
            PropertyManagementRent.objects.filter(
                agent_uuid=agent_data.agent_uuid
            ).values_list('pk', flat=True)
        )
        sale_ids = set(
            PropertyManagementSale.objects.filter(
                agent_uuid=agent_data.agent_uuid
            ).values_list('pk', flat=True)
        )
        house_count = len(rent_ids) + len(sale_ids)
        has_listing = house_count > 0

        # ── Leads ─────────────────────────────────────────────────────────────
        # Fetch once, reuse for count, new_lead_count, and recent_inquiries.
        # date_created is a DateField so compare with date() not datetime.
        leads         = LeadInfo.objects.filter(agent_id=agent_data.agent_uuid)
        lead_count    = leads.count()
        new_leads     = leads.filter(date_created=timezone.now().date())
        new_lead_count = new_leads.count()

        # ── Appointments ──────────────────────────────────────────────────────
        today_appointments = Appointments.objects.filter(
            agent_uuid=agent_data.agent_uuid,
            appointment=timezone.now().date()
        )

        # ── Rating ────────────────────────────────────────────────────────────
        rating_data = AgentRating.objects.filter(
            agent_uuid=agent_data.agent_uuid
        ).aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))

        average_rating = rating_data['avg_rating'] or 0.0
        total_reviews  = rating_data['total_reviews']

        # ── Company name — only query if agent belongs to a company ──────────
        # Avoids the query entirely for solo agents
        company_name = None
        if agent_data.company_uuid:
            try:
                company      = CompanyInformation.objects.get(
                    unique_company_id=agent_data.company_uuid
                )
                company_name = company.company_name
            except CompanyInformation.DoesNotExist:
                company_name = None

        # ── Profile strength ──────────────────────────────────────────────────
        has_picture = bool(agent_data.profile_picture)
        has_phone   = bool(agent_data.phone_number)

        return render(request, 'agent/dashboard.html', {
            'agent_info':            agent_data,
            'name':                  agent_name,
            'first_name':            first_name,
            'work_type':             agent_data.work_type,
            'email':                 agent_data.email,
            'phone':                 agent_data.phone_number,
            'location':              agent_data.location,
            'greeting':              greeting,
            'tips':                  quote['tips'],
            'by':                    quote['by'],
            'house_count':           house_count,
            'lead_count':            lead_count,
            'new_lead_count':        new_lead_count,
            'recent_inquiries':      leads.order_by('-date_created')[:5],
            'todays_appointment':    today_appointments,
            'avg_rating':            average_rating,
            'total_reviews':         total_reviews,
            'company_name':          company_name,
            'has_headshot':          has_picture,
            'has_whatsapp':          has_phone,
            'has_listing':           has_listing,
            'agent_profile_strength': calculate_agent_profile_strength(
                                          has_picture, has_listing, has_phone
                                      ),
        })

    except AgentInformation.DoesNotExist:
        messages.error(request, 'Set up your profile to access other pages')
        return redirect('agent:agent-form')

    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})




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
                messages.error(request, f'Main form errors: {form.errors}')
            
            if not exp_valid:
                messages.error(request, f'Experience errors: {exp_link.errors}')
            
            if not soc_valid:
                messages.error(request, f'Social links errors: {soc_form.errors}')
            
            # If all forms are valid, save them
            if form_valid and exp_valid and soc_valid:
                try:
                    with transaction.atomic():
                        # Save the main agent form
                        agent = form.save(commit=False)
                        agent.user_id = request.user.id
                        agent.users = request.user
                        agent.first_name = request.user.first_name
                        agent.last_name  = request.user.last_name 
                        # Handle universal_agent checkbox
                        agent.universal_agent = request.POST.get('universal_agent') == 'on'
                        
                        agent.save()
                        
                        # Save experience formset
                        experiences = exp_link.save(commit=False)
                        for exp in experiences:
                            exp.agent = agent
                            exp.save()
                        
                        # Handle deleted experiences
                        for exp in exp_link.deleted_objects:
                            exp.delete()
                        
                        
                        # Save social links formset
                        socials = soc_form.save(commit=False)
                        for social in socials:
                            social.agent = agent
                            social.save()
                        
                        # Handle deleted social links
                        for social in soc_form.deleted_objects:
                            social.delete()
                        
                        
                        
                        messages.success(request, 'Profile created successfully!')
                        return HttpResponseRedirect(f"{request.path}?submitted=True")
                        
                except Exception as e:
                    print(f"Error saving agent data")
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
            'name': f'{agent.first_name} {agent.last_name}' if hasattr(agent, 'first_name') else agent.user.get_full_name(),
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

        analytics_data, _ = AgentAnalytics.objects.get_or_create(
            agent=current_agent,
            defaults={
                'profile_views':         0,
                'property_views_l':      0,
                'property_views_s':      0,
                'average_profile_views': 0,
                'average_lease_views':   0,
                'average_sale_views':    0,
                'monthly_leads':         0,
                'monthly_reviews':       0,
                'average_leads':         0,
                'average_reviews':       0,
                'ratings':               0.0,
                'reviews':               0,
                'competition':           0.0,
            }
        )

        # ── 30-day window start ──────────────────────────────────────────────
        # The cron job moves this forward every 30 days.
        # Every date-filtered query below uses this as its starting point.
        window_start = analytics_data.last_reset_date

        # ── Property IDs — fetched once, reused below ────────────────────────
        rent_ids = set(
            PropertyManagementRent.objects.filter(
                agent_uuid=current_agent.agent_uuid
            ).values_list('pk', flat=True)
        )
        sale_ids = set(
            PropertyManagementSale.objects.filter(
                agent_uuid=current_agent.agent_uuid
            ).values_list('pk', flat=True)
        )

        # ── Property views — PropertyViews gets wiped by cron, no date filter
        lease_views = PropertyViews.objects.filter(
            property_type='Rent',
            property_id__in=rent_ids
        ).count()

        sale_views = PropertyViews.objects.filter(
            property_type='Sale',
            property_id__in=sale_ids
        ).count()

        # ── Leads — filtered to current 30-day window ────────────────────────
        monthly_leads = LeadInfo.objects.filter(
            agent_id=current_agent.agent_uuid,
            date_created__gte=window_start
        ).count()

        # ── Ratings — all-time for display, monthly count for tracking ───────
        all_time_rating = AgentRating.objects.filter(
            agent_uuid=current_agent.agent_uuid
        ).aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))

        monthly_reviews = AgentRating.objects.filter(
            agent_uuid=current_agent.agent_uuid,
            created_at__gte=window_start
        ).count()

        average_rating = all_time_rating['avg_rating'] or 0.0
        total_reviews  = all_time_rating['total_reviews']

        # ── Appointments — filtered to current 30-day window ─────────────────
        monthly_appointments = Appointments.objects.filter(
            agent_uuid=current_agent.agent_uuid,
            appointment__gte=window_start
        ).count()

        # ── Update analytics — views read from DB each load, cron resets ─────
        analytics_data.property_views_l = lease_views
        analytics_data.property_views_s = sale_views
        analytics_data.monthly_leads    = monthly_leads
        analytics_data.monthly_reviews  = monthly_reviews
        analytics_data.ratings          = average_rating
        analytics_data.reviews          = total_reviews

        # ── Percentage changes vs last month's rolling average ────────────────
        lease_views_change   = monthly_change(lease_views, analytics_data.average_lease_views)
        sale_views_change    = monthly_change(sale_views, analytics_data.average_sale_views)
        profile_views_change = monthly_change(analytics_data.profile_views, analytics_data.average_profile_views)
        leads_change         = monthly_change(monthly_leads, analytics_data.average_leads)
        reviews_change       = monthly_change(monthly_reviews, analytics_data.average_reviews)
        total_prop_incr_perc = (sale_views_change + lease_views_change) / 2

        # ── Competition loop — bulk queries, zero per-agent DB hits ──────────
        all_analytics = AgentAnalytics.objects.select_related('agent').all()

        # One query: total likes per agent_uuid across all rent properties
        rent_likes_by_agent = {
            item['agent_uuid']: item['total']
            for item in PropertyManagementRent.objects.values('agent_uuid')
            .annotate(total=Sum('total_likes'))
        }
        sale_likes_by_agent = {
            item['agent_uuid']: item['total']
            for item in PropertyManagementSale.objects.values('agent_uuid')
            .annotate(total=Sum('total_likes'))
        }

        total_agents_eng      = []
        current_agent_score   = 0.0

        for record in all_analytics:
            uid = record.agent.agent_uuid

            ag_total_likes = (
                (rent_likes_by_agent.get(uid) or 0) +
                (sale_likes_by_agent.get(uid) or 0)
            )
            ag_rating_score   = (record.ratings or 0) * (record.reviews or 0)
            ag_avg_prop_views = record.average_sale_views + record.average_lease_views

            ag_eng_rate = engagement_rate(
                ag_total_likes,
                ag_avg_prop_views,
                record.average_profile_views,
                ag_rating_score
            )
            total_agents_eng.append(ag_eng_rate)

            # Capture current agent score without an extra save inside the loop
            if record.agent.id == current_agent.id:
                current_agent_score = ag_eng_rate

        # Save all updated fields in one single DB write
        analytics_data.competition = current_agent_score
        analytics_data.save()

        # ── Market position ───────────────────────────────────────────────────
        if total_agents_eng and len(total_agents_eng) > 1:
            sorted_eng   = sorted(total_agents_eng, reverse=True)
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
            top_performer   = "New Agent"
            market_position = 100

        avg_prop_views = analytics_data.average_lease_views + analytics_data.average_sale_views
        total_eng_sum  = sum(total_agents_eng)

        calculated_engagement = total_agents_engagement_calculator(
            total_eng_sum,
            current_agent_score,
            current_agent.agent_uuid,
            avg_prop_views
        )

        competition_pct = calculated_engagement[0]
        inq_conv_rate   = calculated_engagement[1]

        # ── Top 4 properties — two queries instead of one per property ────────
        agent_props_rent = list(PropertyManagementRent.objects.filter(
            agent_uuid=current_agent.agent_uuid
        ))
        agent_props_sale = list(PropertyManagementSale.objects.filter(
            agent_uuid=current_agent.agent_uuid
        ))

        all_properties = agent_props_rent + agent_props_sale
        all_properties.sort(key=lambda x: x.total_likes, reverse=True)
        top_properties = all_properties[:4]

        top_rent_ids = [p.pk for p in top_properties if p in agent_props_rent]
        top_sale_ids = [p.pk for p in top_properties if p in agent_props_sale]

        rent_view_counts = {
            item['property_id']: item['cnt']
            for item in PropertyViews.objects.filter(
                property_type='Rent',
                property_id__in=top_rent_ids
            ).values('property_id').annotate(cnt=Count('id'))
        }
        sale_view_counts = {
            item['property_id']: item['cnt']
            for item in PropertyViews.objects.filter(
                property_type='Sale',
                property_id__in=top_sale_ids
            ).values('property_id').annotate(cnt=Count('id'))
        }

        view_list = []
        for prop in top_properties:
            if prop in agent_props_rent:
                view_list.append(rent_view_counts.get(prop.pk, 0))
            else:
                view_list.append(sale_view_counts.get(prop.pk, 0))

        likes_views = zip(top_properties, view_list)

        return render(request, 'agent/agent_analytics.html', {
            'profile_views':        analytics_data.profile_views,
            'listing_views':        analytics_data.property_views_l + analytics_data.property_views_s,
            'lease_views':          analytics_data.property_views_l,
            'sale_views':           analytics_data.property_views_s,
            'profile_incr_perc':    profile_views_change,
            'lease_incr_perc':      lease_views_change,
            'sale_incr_perc':       sale_views_change,
            'total_prop_incr_perc': total_prop_incr_perc,
            'monthly_leads':        monthly_leads,
            'leads_change':         leads_change,
            'monthly_reviews':      monthly_reviews,
            'reviews_change':       reviews_change,
            'monthly_appointments': monthly_appointments,
            'average_rating':       average_rating,
            'total_reviews':        total_reviews,
            'competition':          top_performer,
            'market_position':      round(market_position, 1),
            'inq_rate':             inq_conv_rate,
            'ranking':              likes_views,
            'window_start':         window_start,
        })

    except AgentInformation.DoesNotExist:
        messages.error(request, 'Agent profile not found.')
        return redirect('landing')

    except Exception as e:
        print(f"Error in analytics view: {e}")
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












def job_listings(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login required')
        return redirect('login')
    if request.user.role != 'agent':
        messages.info(request, 'Agents Only')
        return redirect('landing')
    
    try:
        jobs = JobPost.objects.all()
        today = datetime.now().date()

        # No set here — we need one result per job, duplicates included
        market_days = [(today - job.date_posted).days for job in jobs]

        return render(request, 'agent/job_listings.html', {
            'jobs': zip(jobs, market_days)
        })
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})


def job_detail(request, job_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    try:
        job=JobPost.objects.get(pk=job_id)
        return render(request, 'agent/job_detail.html', {'job':job})
    except ObjectDoesNotExist:
        messages.info(request, 'Error Job Data not found')
    except Exception as e:
        messages.error(request, 'Tell us the error')
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
        ratings=AgentRating.objects.filter(agent_uuid=agent_data.agent_uuid)
        try:
            lease_properties.delete()
            sale_properties.delete()
            property_views.delete()
            appointments.delete()
            leads.delete()
            ratings.delete()
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








def join_via_invite(request):
    """
    Agent lands here after clicking the invite link.
    URL looks like:  /invite/join/?token=<uuid>
    """

    # ── 1. Pull token from query string ──────────────────────
    token = request.GET.get('token')

    if not token:
        messages.error(request, 'Invalid invite link — no token provided.')
        return redirect('landing')

    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to use this invite link.')
        return redirect(f"{reverse('login')}?next={request.get_full_path()}")

    if request.user.role != 'agent':
        messages.info(request, 'Only agents can join via invite link.')
        return redirect('landing')

    try:
        agent = AgentInformation.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        messages.info(
            request,
            'Please complete your agent profile first before joining a company.'
        )
        return redirect('agent:setup-profile')

    try:
        invite_link = InviteLink.objects.get(invite_token=token)
    except ObjectDoesNotExist:
        messages.error(request, 'This invite link is invalid or broken.')
        return redirect('landing')

    if not invite_link.is_active:
        messages.info(request, 'This invite link has been deactivated.')
        return redirect('landing')

    if timezone.now() >= invite_link.expires_at:
        messages.info(request, 'This invite link has expired.')
        return redirect('landing')

    if invite_link.max_uses is not None and invite_link.use_count >= invite_link.max_uses:
        messages.info(request, 'This invite link has reached its maximum uses.')
        return redirect('landing')

    # ── Agent must not already be in any company ──────────────
    if agent.company_uuid:
        messages.info(
            request,
            'You already belong to a company. '
            'You can only be part of one company at a time.'
        )
        return redirect('agent:dashboard')

    # ── Agent must not already be in THIS specific company ────
    company = invite_link.company

    if Employees.objects.filter(agent_uuid=agent.agent_uuid).exists():
        messages.info(request, f"You've already joined {company.company_name}.")
        return redirect('agent:dashboard')

    # ── All checks passed — onboard the agent ─────────────────
    try:
        Employees.objects.create(
            company=company,
            agent_name=f'{agent.first_name} {agent.last_name}',
            company_department='Unassigned',
            company_role=agent.work_type,
            agent_email=agent.email,
            agent_phone_no=agent.phone_number,
            agent_uuid=agent.agent_uuid,
            agent_headshot=agent.profile_picture,
        )

        agent.company_uuid = company.unique_company_id
        agent.save()

        invite_link.use_count += 1
        invite_link.save(update_fields=['use_count'])

        CompanyActivityLog.objects.create(
            company=company,
            action=f'Agent {agent.first_name} joined the team via invite link.'
        )

        messages.success(
            request,
            f"Congrats on your new job at {company.company_name}! 🎉"
        )
        return redirect('agent:dashboard')

    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})