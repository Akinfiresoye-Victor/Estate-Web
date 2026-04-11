from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import *
from django.http import HttpResponseRedirect, JsonResponse
from django.db import transaction
from companies.models import CompanyInformation, CompanyActivityLog
from . import news_scrape as ns
from agents.models import AgentInformation
from estate.models import LeadInfo
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from core.utils import *
from .models import ErrorLog
import traceback
from django.utils.http import url_has_allowed_host_and_scheme
from landlord.models import LandlordInformation
from django_ratelimit.decorators import ratelimit
from django.core.mail import send_mail

def landing_page(request):
    if not request.user.is_authenticated:
        return render(request, 'core/landing.html')
    
    # 1. Grab the potential redirect URL
    next_url = request.GET.get('next') or request.POST.get('next')
    
    # 2. Run the security check ONCE
    is_safe = url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ) if next_url else False

    # 3. Handle role-based redirects
    if request.user.role == 'company':
        return redirect(next_url if is_safe else 'company:dashboard')
        
    elif request.user.role == 'agent':
        return redirect(next_url if is_safe else 'agent:dashboard')
        
    elif request.user.role == 'customer':
        return redirect(next_url if is_safe else 'customer:user-profile')
    
    elif request.user.role == 'landlord':
        return redirect(next_url if is_safe else 'landlord:dashboard')
        
    else:
        return render(request, 'core/landing.html')

def about_page(request):
    return render(request, 'core/about.html')



'''Users Feedbacks'''
def feedbacks(request):
    try:
        submitted = False
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        elif user_role == 'landlord':
            base_template = 'landlord/base.html'
        else:
            base_template='estate/base.html'
        if request.method == 'POST':
            messages.success(request, 'Thank you for your feedback!')
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
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


'''New Multi-Channel Feedback System — receives AJAX POST from the feedback modal'''
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
@require_POST
def submit_feedback(request):
    try:
        reaction   = request.POST.get('reaction',  '').strip()
        category   = request.POST.get('category',  '').strip()
        details    = request.POST.get('details',   '').strip()
        role       = request.POST.get('role',      '').strip()
        screenshot = request.FILES.get('screenshot', None)

        if not reaction or not category:
            messages.error(request, 'Please provide both a reaction and a category.')
            return HttpResponse(status=400)

        try:
            reaction_int = int(reaction)
            if reaction_int not in range(1, 6):
                raise ValueError
        except ValueError:
            messages.error(request, 'The reaction value provided is invalid.')
            return HttpResponse(status=400)

        valid_categories = ['bug', 'feature', 'complaint', 'praise']
        if category not in valid_categories:
            messages.error(request, 'The selected category is invalid.')
            return HttpResponse(status=400)

        valid_roles = ['agent', 'company', 'admin', 'landlord']
        if role not in valid_roles:
            role = None


        feedback_obj = Feedbacks(
            reaction   = reaction_int,
            category   = category,
            details    = details,
            role       = role,
            screenshot = screenshot,
        )

        if request.user.is_authenticated:
            feedback_obj.user = request.user

        feedback_obj.save()

        messages.success(request, 'Thank you for your feedback! We value your input.')
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])  
        else:
            messages.error(request, 'Unable to complete the redirection.')
            return redirect('landing')

    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
'''Property Management'''

def sell_property(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
 
    if request.user.role == 'customer':
        messages.info(request, 'You cannot list properties as a customer. Please log in as a Landlord or Agent.')
        return redirect('landing')
    try:
        user_role = request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        elif user_role == 'landlord':
            base_template = 'landlord/base.html'
        else:
            base_template = 'estate/base.html'
            
        if request.user.role == 'agent':
            try:
                agent=AgentInformation.objects.get(user=request.user)
            except ObjectDoesNotExist:
                messages.info(request, 'Please complete your profile setup.')
                return redirect('agent:agent-form')
            company=get_agent_company(agent)
            
            allowed, reason= can_add_to_inventory(agent, company)
            if not allowed:
                messages.error(request, reason)
                return redirect('listings')
        elif request.user.role == 'company':
            """
            Company listed themselves
            """
            try:
                company=CompanyInformation.objects.get(user=request.user)
            except ObjectDoesNotExist:
                messages.info(request, 'Please complete your profile setup.')
                return redirect('company:company_form')
            agent=None
            allowed, reason= can_add_to_inventory(agent, company)
            if not allowed:
                messages.error(request, reason)
                return redirect('listings')
        elif request.user.role == 'landlord':
            from landlord.models import LandlordInformation
            try:
                landlord_info = LandlordInformation.objects.get(user=request.user)
            except ObjectDoesNotExist:
                messages.info(request, 'Please complete your profile setup.')
                return redirect('landlord:profile-setup')
            allowed, reason = can_add_to_inventory(agent=None, company=None, landlord=landlord_info)
            if not allowed:
                messages.error(request, reason)
                return redirect('landlord:inventory')
        else:
            messages.info(request, 'An error occured')
            return redirect('landing')
        submitted = False
 
        if request.method == 'POST':
            prop_form  = SellForm(request.POST or None, request.FILES or None)
            image_form = SaleImageFormSet(request.POST or None, request.FILES or None)
 
            if prop_form.is_valid() and image_form.is_valid():
                with transaction.atomic():
                    landlord = prop_form.save(commit=False)
                    category = prop_form.cleaned_data.get('property_category')
 
                    # Clear non-selected category fields
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
                        company = CompanyInformation.objects.get(user=request.user)
                        landlord.company_uuid  = company.unique_company_id
                        landlord.user       = request.user
                        landlord.time_stamp    = timezone.now()
                        landlord.is_listed=False
                        landlord.save()
 
                        image_form.instance = landlord
                        image_form.save()
 
                        # ── Initial scoring ──────────────────────────
                        score_new_listing(landlord, 'Sale')
 
                        CompanyActivityLog.objects.create(
                            company=company,
                            action='Property Listed'
                        )
 
                    except CompanyInformation.DoesNotExist:
                        try:
                            agent = AgentInformation.objects.get(user=request.user)
                            landlord.agent_uuid   = str(agent.agent_uuid)
                            if agent.company_uuid:
                                landlord.company_uuid = agent.company_uuid
                            landlord.user= request.user
                            landlord.time_stamp= timezone.now()
                            landlord.is_listed=False
                            landlord.save()
    
                            image_form.instance = landlord
                            image_form.save()
    
                            # ── Initial scoring ──────────────────────────
                            score_new_listing(landlord, 'Sale')
                        except AgentInformation.DoesNotExist:
                            from landlord.models import LandlordInformation
                            landlord_info = LandlordInformation.objects.get(user=request.user)
                            landlord.landlord_uuid = str(landlord_info.landlord_uuid)
                            landlord.user = request.user
                            landlord.time_stamp = timezone.now()
                            landlord.is_listed = False
                            landlord.save()
                            
                            image_form.instance = landlord
                            image_form.save()
                            score_new_listing(landlord, 'Sale')
 
                return HttpResponseRedirect('?submitted=True')
 
            else:
                return render(request, 'estate/error_page.html', {'e': prop_form.errors})
 
        else:
            prop_form  = SellForm()
            image_form = SaleImageFormSet()
            if 'submitted' in request.GET:
                submitted = True
 
        context = {
            'form':          prop_form,
            'image_form':    image_form,
            'submitted':     submitted,
            'base_template': base_template,
        }
        return render(request, 'core/sell_property.html', context)
 
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
 
 
# ─────────────────────────────────────────────────────────────────────────────
# lease_property
# ─────────────────────────────────────────────────────────────────────────────
 
def lease_property(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
 
    if request.user.role == 'customer':
        messages.info(request, 'You cannot list properties as a customer. Please log in as a Landlord or Agent.')
        return redirect('landing')
 
    try:
        submitted  = False
        user_role  = request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        elif user_role == 'landlord':
            base_template = 'landlord/base.html'
        else:
            base_template = 'estate/base.html'
        if request.user.role == 'agent':
            try:
                agent=AgentInformation.objects.get(user=request.user)
            except ObjectDoesNotExist:
                messages.info(request, 'Please complete your profile setup.')
                return redirect('agent:agent-form')
            company=get_agent_company(agent)
            
            allowed, reason= can_add_to_inventory(agent, company)
            if not allowed:
                messages.error(request, reason)
                return redirect('listings')
        elif request.user.role == 'company':
            """
            Company listed themselves
            """
            try:
                company=CompanyInformation.objects.get(user=request.user)
            except ObjectDoesNotExist:
                messages.info(request, 'Please complete your profile setup.')
                return redirect('company:company_form')
            agent=None
            allowed, reason= can_add_to_inventory(agent, company)
            if not allowed:
                messages.error(request, reason)
                return redirect('listings')
        elif request.user.role == 'landlord':
            from landlord.models import LandlordInformation
            try:
                landlord_info = LandlordInformation.objects.get(user=request.user)
            except ObjectDoesNotExist:
                messages.info(request, 'Please complete your profile setup.')
                return redirect('landlord:profile-setup')
            allowed, reason = can_add_to_inventory(agent=None, company=None, landlord=landlord_info)
            if not allowed:
                messages.error(request, reason)
                return redirect('landlord:inventory')
        submitted=False
        if request.method == 'POST':
            prop_form  = LeaseForm(request.POST or None, request.FILES or None)
            image_form = RentImageFormSet(request.POST or None, request.FILES or None)
 
            if prop_form.is_valid() and image_form.is_valid():
                with transaction.atomic():
                    landlord = prop_form.save(commit=False)
                    category = prop_form.cleaned_data.get('property_category')
 
                    # Clear non-selected category fields
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
                        company = CompanyInformation.objects.get(user=request.user)
                        landlord.company_uuid  = company.unique_company_id
                        landlord.user       = request.user
                        landlord.time_stamp    = timezone.now()
                        landlord.is_listed=False
                        landlord.save()
 
                        image_form.instance = landlord
                        image_form.save()
 
                        # ── Initial scoring ──────────────────────────
                        score_new_listing(landlord, 'Rent')
 
                        CompanyActivityLog.objects.create(
                            company=company,
                            action='Property Listed'
                        )
 
                    except CompanyInformation.DoesNotExist:
                        try:
                            agent = AgentInformation.objects.get(user=request.user)
                            landlord.agent_uuid = agent.agent_uuid
                            if agent.company_uuid is not None:
                                landlord.company_uuid = agent.company_uuid
                            landlord.user      = request.user
                            landlord.time_stamp   = timezone.now()
                            landlord.is_listed=False
                            landlord.save()
     
                            image_form.instance = landlord
                            image_form.save()
     
                            # ── Initial scoring ──────────────────────────
                            score_new_listing(landlord, 'Rent')
                        except AgentInformation.DoesNotExist:
                            from landlord.models import LandlordInformation
                            landlord_info = LandlordInformation.objects.get(user=request.user)
                            landlord.landlord_uuid = str(landlord_info.landlord_uuid)
                            landlord.user = request.user
                            landlord.time_stamp = timezone.now()
                            landlord.is_listed = False
                            landlord.save()
                            
                            image_form.instance = landlord
                            image_form.save()
                            score_new_listing(landlord, 'Rent')
 
                return HttpResponseRedirect('?submitted=True')
 
            else:
                return render(request, 'estate/error_page.html', {'e': prop_form.errors})
 
        else:
            prop_form  = LeaseForm()
            image_form = RentImageFormSet()
            if 'submitted' in request.GET:
                submitted = True
 
        context = {
            'form':          prop_form,
            'image_form':    image_form,
            'submitted':     submitted,
            'base_template': base_template,
        }
        return render(request, 'core/lease_property.html', context)
 
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})        


@ratelimit(key='ip', rate='30/m', method='POST', block=True)
def toggle_listing(request, property_id, property_type):
    """
    Toggles a property between inventory (private) and listed(public).
    Supports AJAX
    """
    is_ajax=request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    Model=PropertyManagementSale if property_type == 'sale' else PropertyManagementRent
    try:
        #making the user who posted have access to the property
        if request.user.role == 'company':
            company=CompanyInformation.objects.filter(user=request.user).values_list('unique_company_id', flat=True).first()
            prop=Model.objects.get(pk=property_id, company_uuid=company)
        elif request.user.role == 'landlord':
            from landlord.models import LandlordInformation
            landlord=LandlordInformation.objects.filter(user=request.user).values_list('landlord_uuid', flat=True).first()
            prop=Model.objects.get(pk=property_id, landlord_uuid=landlord)
        else:
            agent=AgentInformation.objects.filter(user=request.user).values_list('agent_uuid', flat=True).first()
            prop=Model.objects.get(pk=property_id, agent_uuid=agent)
    except:
        if is_ajax:
            return JsonResponse({'error':'Not found'}, status=404)
        messages.error(request, 'The requested property could not be found.')
        return redirect('listings')

    if prop.is_listed:
        prop.is_listed = False
        prop.save(update_fields=['is_listed'])
        msg = 'Property moved to inventory.'
        if is_ajax:
            # Calculate new live count based on user role
            try:
                if request.user.role == 'landlord':
                    from landlord.models import LandlordInformation
                    landlord_obj = LandlordInformation.objects.get(user=request.user)
                    live_count = get_listing_count(None, None, landlord_obj)
                elif request.user.role == 'company':
                    company_obj = CompanyInformation.objects.get(user=request.user)
                    live_count = get_listing_count(None, company_obj)
                else: # agent
                    agent_obj = AgentInformation.objects.get(user=request.user)
                    live_count = get_listing_count(agent_obj)
            except Exception:
                live_count = 0  # Fallback
            return JsonResponse({'is_listed': False, 'message': msg, 'live_count': live_count})
        messages.success(request, msg)
    else:
        # Determine roles for can_go_live check
        agent_obj = None
        company_obj = None
        landlord_obj = None

        if request.user.role == 'agent':
            agent_obj = AgentInformation.objects.get(user=request.user)
            company_obj = get_agent_company(agent_obj)
        elif request.user.role == 'company':
            company_obj = CompanyInformation.objects.get(user=request.user)
        elif request.user.role == 'landlord':
            from landlord.models import LandlordInformation
            landlord_obj = LandlordInformation.objects.get(user=request.user)
        
        allowed, reason = can_go_live(agent=agent_obj, company=company_obj, landlord=landlord_obj)
        if not allowed:
            if is_ajax:
                return JsonResponse({'error': reason}, status=403)
            messages.error(request, reason)
            return redirect('listings')

        prop.is_listed = True
        prop.save(update_fields=['is_listed'])
        msg = 'Your property is now live!'
        if is_ajax:
            live_count = get_listing_count(agent_obj, company_obj, landlord_obj)
            return JsonResponse({'is_listed': True, 'message': msg, 'live_count': live_count})
        messages.success(request, msg)
    return redirect('listings')



'''News Blog Automation'''
def articles(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
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
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})





#view to update listed property on rent
def update_property_rent(request, property_id):
    # 1. Quick Authentication Guard
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('landing')
    
    if request.user.role == 'customer':
        messages.info(request, 'This feature is coming soon!')
        return redirect('landing')

    # 2. Fetch the object safely
    property_obj = get_object_or_404(PropertyManagementRent, pk=property_id)
    user_role = request.user.role
    
    # 3. Map templates to roles (Cleaner than if/elif)
    template_map = {
        'company': 'company/base.html',
        'agent': 'agent/base.html',
        'landlord': 'landlord/base.html',
    }
    base_template = template_map.get(user_role, 'estate/base.html')

    try:
        # 4. Centralized Authorization Logic
        is_authorized = False
        
        if user_role == 'agent':
            agent_uuid = AgentInformation.objects.filter(user=request.user).values_list('agent_uuid', flat=True).first()
            is_authorized = (property_obj.agent_uuid == agent_uuid)
            
        elif user_role == 'company':
            company = CompanyInformation.objects.filter(user=request.user).first()
            if company:
                is_authorized = (property_obj.company_uuid == company.unique_company_id)
                if is_authorized and request.method == 'POST':
                    CompanyActivityLog.objects.create(company=company, action='Property Listing Updated')

        elif user_role == 'landlord':
            landlord_uuid = LandlordInformation.objects.filter(user=request.user).values_list('landlord_uuid', flat=True).first()
            is_authorized = (property_obj.landlord_uuid == landlord_uuid)

        # Final check: If role isn't recognized or ownership fails
        if not is_authorized:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect(request.META.get('HTTP_REFERER', 'landing'))

        # 5. Form Handling
        prop_form = LeaseForm(request.POST or None, request.FILES or None, instance=property_obj)
        image_form = RentImageFormSet(request.POST or None, request.FILES or None, instance=property_obj)

        if request.method == 'POST':
            if prop_form.is_valid() and image_form.is_valid():
                prop_form.save()
                image_form.save()
                messages.success(request, "Property updated successfully.")
                return redirect('listings')

        context = {
            'property': property_obj,
            'form': prop_form,
            'images': image_form,
            'base_template': base_template
        }
        return render(request, 'core/update_property.html', context)

    except Exception:
        # Log the error and show the error page
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


#view to update listed property on rent
def update_property_sale(request, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.info(request, 'This feature is coming soon!')
        return redirect('landing')
    try:
        #updating the particular listing that needs to be updated using the property id
        property=PropertyManagementSale.objects.get(pk= property_id)
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        elif user_role == 'landlord':
            base_template = 'landlord/base.html'
        else:
            base_template='estate/base.html'
        #limiting update access to owner of listings
        if user_role == 'agent':
            agent_uuid=AgentInformation.objects.filter(user=request.user).values_list('agent_uuid', flat=True).first()
            if property.agent_uuid != agent_uuid:
                messages.warning(request, 'Access denied: Unauthorized action.')
                if 'HTTP_REFERER' in request.META:
                    return redirect(request.META['HTTP_REFERER'])  
                else:
                    return redirect('landing')
        elif user_role == 'company':
            company=CompanyInformation.objects.get(user=request.user)
            if property.company_uuid != company.unique_company_id:
                messages.warning(request, 'Access denied: Unauthorized action.')
                if 'HTTP_REFERER' in request.META:
                    return redirect(request.META['HTTP_REFERER'])  
                else:
                    return redirect('landing')
            CompanyActivityLog.objects.create(
                company=company,
                action= 'Property Listing Updated'
            )
        elif user_role == 'landlord':
            landlord_uuid=LandlordInformation.objects.filter(user=request.user).values_list('landlord_uuid', flat=True).first()
            if property.landlord_uuid !=landlord_uuid :
                messages.warning(request, 'Access denied: Unauthorized action.')
                if 'HTTP_REFERER' in request.META:
                    return redirect(request.META['HTTP_REFERER'])  
                else:
                    return redirect('landing')
        else:
            messages.info(request, 'Coming soon!')
            return redirect('landing')
        prop_form= SellForm(request.POST or None, request.FILES or None, instance=property)
        image_form = SaleImageFormSet(request.POST or None, request.FILES or None, instance=property)
        if prop_form.is_valid() and image_form.is_valid():
            prop_form.save()
            image_form.save()
            messages.success(request, "Property updated successfully.")
            return redirect('listings')
        return render(request, 'core/update_property_s.html', {'property': property, 'form': prop_form,'images': image_form, 'base_template':base_template})
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


#view to delete listings
def delete_property_on_lease(request, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        if request.user.role == 'company':
            company=CompanyInformation.objects.get(user=request.user)
            agent_uuid=None
            landlord_uuid=None
        elif request.user.role == 'agent':
            agent_uuid=AgentInformation.objects.filter(user=request.user).values_list('agent_uuid', flat=True).first()
            company=None
            landlord_uuid=None
        elif request.user.role == 'landlord':
            landlord_uuid=LandlordInformation.objects.filter(user=request.user).values_list('landlord_uuid', flat=True).first()
            company=None
            agent_uuid=None
        else:
            messages.info(request, 'Error... You dont have the feature')
            return redirect('landing')

        property1= PropertyManagementRent.objects.get(pk=property_id)
        #Additional layer of security
        if company and (property1.company_uuid != company.unique_company_id):
            CompanyActivityLog.objects.create(
                company=company,
                action= 'Property Listing Deleted'
            )
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        elif agent_uuid and (property1.agent_uuid != agent_uuid):
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        elif landlord_uuid and (property1.landlord_uuid != landlord_uuid):
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        
        leads=LeadInfo.objects.filter(property_type='Rent', property_intrested=property1.pk)
        appointments=Appointments.objects.filter(property_type='Rent', property_id=property1.pk)
        property_views=PropertyViews.objects.filter(property_type='Rent', property_id=property1.pk)
        wishlists=WishlistStorageUnit.objects.filter(property_type='Rent', property_id=property1.pk)
        if appointments:
            for appointment in appointments:
                appointment.property_id=None
                appointment.property_type='Property Deleted'
                appointment.save()
        if leads:
            for lead in leads:
                lead.property_intrested=None
                lead.save()
        try:
            wishlists.delete()
            property_views.delete()
            property1.delete()
            messages.success(request, "Property deleted successfully.")
            return redirect('listings')
        except Exception:
            messages.error(request, 'An unexpected error occurred. Please try again.')
    except ObjectDoesNotExist:
        messages.error(request, 'Property Data Not Found')
        return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})

#view to delete listings
def delete_property_on_sale(request, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.warning(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:    
        if request.user.role == 'company':
            company=CompanyInformation.objects.get(user=request.user)
            agent_uuid=None
            landlord_uuid=None
        elif request.user.role == 'agent':
            agent_uuid=AgentInformation.objects.filter(user=request.user).values_list('agent_uuid', flat=True).first()
            company=None
            landlord_uuid=None
        elif request.user.role == 'landlord':
            landlord_uuid=LandlordInformation.objects.filter(user=request.user).values_list('landlord_uuid', flat=True).first()
            company=None
            agent_uuid=None
        else:
            messages.info(request, 'Coming soon!')
            return redirect('landing')

        property1= PropertyManagementSale.objects.get(pk=property_id)
        
        #Additional layer of security
        if company and property1.company_uuid != company.unique_company_id:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        elif agent_uuid and property1.agent_uuid != agent_uuid:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        elif landlord_uuid and property1.landlord_uuid != landlord_uuid:
            messages.warning(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
        leads=LeadInfo.objects.filter(property_type='Sale', property_intrested=property1.pk)
        appointments=Appointments.objects.filter(property_type='Sale', property_id=property1.pk)
        property_views=PropertyViews.objects.filter(property_type='Sale', property_id=property1.pk)
        wishlists=WishlistStorageUnit.objects.filter(property_type='Sale', property_id=property1.pk)
        for appointment in appointments:
            appointment.property_id=None
            appointment.property_type='Property Deleted'
            appointment.save()
        for lead in leads:
            lead.property_intrested=None
            lead.save()
        wishlists.delete()
        property_views.delete()
        property1.delete()
        messages.success(request, "Property deleted successfully.")
        if request.user.role == 'company':
            CompanyActivityLog.objects.create(
                company=company,
                action= 'Property Listing Deleted'
            )
        return redirect('listings')
    except ObjectDoesNotExist:
        messages.error(request, 'Property Data Not Found')
        return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})






def partner_with_us(request):
    """
    Renders the partnership application form.
    GET  → empty form
    POST → validate, save (including M2M), redirect to success
    """
    if request.method == 'POST':
        form = PartnershipForm(request.POST)

        if form.is_valid():
            partnership = form.save(commit=False)
            partnership.save()           # writes the main row to the database
            form.save_m2m()              # now writes the M2M

            messages.success(
                request,
                "Thank you for applying! Our partnerships team will review your application "
                "and reach out within 3–5 business days."
            )
            return redirect('partner-success')

        else:
            messages.error(
                request,
                "Please correct the errors in the form and resubmit your application."
            )

    else:
        form = PartnershipForm()

    return render(request, 'core/partner.html', {'form': form})


def partner_success(request):
    """Simple success page after a partnership application is submitted."""
    return render(request, 'core/partner_success.html')



def appointment_detail(request,appt_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.info(request, 'Access denied: Unauthorized action.')
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
            company=CompanyInformation.objects.filter(user=request.user).values_list('unique_company_id', flat=True).first()
            sample= Appointments.objects.get(appointment_uuid=appt_uuid)
            if company != sample.company_uuid:
                messages.warning(request, 'Access denied: Unauthorized action.')
                return redirect('appointment')
            appointment=sample
        else:
            agent=AgentInformation.objects.filter(user=request.user).values_list('agent_uuid', flat=True).first()
            sample= Appointments.objects.get(appointment_uuid=appt_uuid)
            if agent != sample.agent_uuid:
                messages.warning(request, 'Access denied: Unauthorized action.')
                return redirect('appointment')
            appointment=sample
        try:
            lead=LeadInfo.objects.get(lead_id=appointment.lead_uuid)
            return render(request, 'core/appointment_detail.html', {'appointment': appointment, 'lead_data': lead, 'base_template':base_template})
        except ObjectDoesNotExist:
            return render(request, 'core/appointment_detail.html', {'appointment': appointment, 'base_template':base_template})
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def add_schedule(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    
    if request.user.role == 'customer':
        messages.error(request, 'Access denied: Unauthorized action.')
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
                    company=CompanyInformation.objects.get(user=request.user)
                    appointment.company_uuid = str(company.unique_company_id)
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Appointment Created'
                    )
                elif request.user.role == 'agent':
                    agent=AgentInformation.objects.get(user=request.user)
                    appointment.agent_uuid = str(agent.agent_uuid)
                
                # Handle property selection if provided
                property_id = request.POST.get('property_id')
                property_type = request.POST.get('property_type')
                
                if property_id:
                    try:
                        property_id = int(property_id)
                        if property_id <= 0:
                            raise ValueError
                        appointment.property_id = property_id
                    except (ValueError, TypeError):
                        messages.error(request, 'The property ID provided is invalid.')
                        return render(request, 'core/add_schedule.html', {'form': form, 'base_template': base_template})
                
                if property_type:
                    if property_type not in ['Sale', 'Rent']:
                        messages.error(request, 'The property type provided is invalid.')
                        return render(request, 'core/add_schedule.html', {'form': form, 'base_template': base_template})
                    appointment.property_type = property_type
                
                # Handle lead/customer selection if provided
                lead_uuid = request.POST.get('lead_uuid')
                if lead_uuid:
                    try:
                        lead = LeadInfo.objects.get(lead_id=lead_uuid)
                        # Check if lead belongs to the user
                        if request.user.role == 'company':
                            if lead.company_uuid != str(company.unique_company_id):
                                raise PermissionError
                        elif request.user.role == 'agent':
                            if lead.agent_id != str(agent.agent_uuid):
                                raise PermissionError
                        appointment.lead_uuid = lead_uuid
                    except (LeadInfo.DoesNotExist, PermissionError):
                        messages.error(request, 'The selected lead is invalid.')
                        return render(request, 'core/add_schedule.html', {'form': form, 'base_template': base_template})
                
                appointment.save()
                
                messages.success(request, 'Your appointment has been scheduled successfully.')
                return redirect('appointment') 
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = AppointmentForm()
        
        context = {
            'form': form,
            'base_template':base_template
        }
        
        return render(request, 'core/add_schedule.html', context)
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def appointment(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
            try:
                company= CompanyInformation.objects.filter(user=request.user).values_list('unique_company_id', flat=True).first()
                total_appointment= Appointments.objects.filter(company_uuid=company)
                return render(request, 'core/appointment.html', {'appointments': total_appointment, 'base_template':base_template})
            except ObjectDoesNotExist:
                messages.error(request, 'An error occured')
                return redirect('landing')
        elif user_role == 'agent':
            base_template = 'agent/base.html'
            try:
                agent= AgentInformation.objects.get(user=request.user)
                total_appointment= Appointments.objects.filter(agent_uuid=agent.agent_uuid)
                return render(request, 'core/appointment.html', {'appointments': total_appointment,'base_template':base_template ,'agent_name':f'{agent.first_name} {agent.last_name}'})
            except ObjectDoesNotExist:
                messages.error(request, 'An Error Occured')
                return redirect('landing')
        else:
            base_template='estate/base.html'
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def estate_blog(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        return render(request, 'core/estate_blog.html', {'base_template': base_template})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def manage_listings(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.warning(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        if user_role == 'company':
            company=CompanyInformation.objects.get(user=request.user)
            agent=None
            property_on_lease=PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
            property_on_sale=PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
            role='company'
        elif user_role == 'agent':
            agent=AgentInformation.objects.get(user=request.user)
            company=None
            if agent.company_uuid:
                company=CompanyInformation.objects.get(unique_company_id=agent.company_uuid)
            property_on_lease=PropertyManagementRent.objects.filter(agent_uuid=agent.agent_uuid)
            property_on_sale=PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid)
            role='agent'
        else:
            messages.error(request, 'An unexpected error occurred.')
            return redirect('landing')
        inv_used=get_inventory_count(agent, company)
        live_used= get_listing_count(agent,company)
        if company and company.company_tier == 'enterprise':
            inv_limit='∞'
            live_limit='∞'
        elif company:
            inv_limit=company.inventory_slots
            live_limit=company.listing_slots
        else:
            inv_limit=agent.inventory_slot
            live_limit=agent.listing_slots
        context={
            'on_lease':property_on_lease,
            'role':role,
            'on_sale':property_on_sale,
            'base_template':base_template,
            'inv_used':inv_used,
            'inv_limit':inv_limit,
            'live_used':live_used,
            'live_limit': live_limit
        }
        return render(request, 'core/listings.html', context)
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def edit_appointment(request, appointment_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    
    if request.user.role == 'customer':
        messages.info(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    
    try:
        user_role = request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template = 'estate/base.html'
        
        if request.user.role == 'company':
            company = CompanyInformation.objects.get(user=request.user)
            item= Appointments.objects.filter(company_uuid=company.unique_company_id).get(appointment_uuid=appointment_uuid)
            if item.company_uuid == company.unique_company_id:
                appointment=item
            else:
                messages.warning(request, 'Access denied: Unauthorized action.')
                return redirect('landing')
        else:
            agent = AgentInformation.objects.get(user=request.user)
            item = Appointments.objects.filter(agent_uuid=agent.agent_uuid).get(appointment_uuid=appointment_uuid)
            if item.agent_uuid == agent.agent_uuid:
                appointment= item
            else:
                messages.warning(request, 'Access denied: Unauthorized action.')
                return redirect('landing')
            
        lead = None
        
        try:
            if appointment.lead_uuid:
                lead = LeadInfo.objects.get(lead_id=appointment.lead_uuid)
        except ObjectDoesNotExist:
            return render(request, 'error/error_page.html', {'e':'The requested lead could not be found.'})
        
        if request.method == 'POST':
            try:
                appointment_date = request.POST.get('appointment_date')
                if not appointment_date:
                    messages.error(request, 'Please provide an appointment date.')
                    return render(request, 'core/edit_appointment.html', {'appointment': appointment, 'lead_data': lead, 'base_template': base_template, 'appointment_types': appointment_types})
                
                try:
                    from datetime import datetime
                    datetime.strptime(appointment_date, '%Y-%m-%d')
                    appointment.appointment = appointment_date
                except ValueError:
                    messages.error(request, 'The appointment date format is invalid.')
                    return render(request, 'core/edit_appointment.html', {'appointment': appointment, 'lead_data': lead, 'base_template': base_template, 'appointment_types': appointment_types})
                
                appointment.note = request.POST.get('note', 'No Note Provided')
                
                appointment_type = request.POST.get('appointment_type')
                if appointment_type not in dict(APPOINTMENT_TYPE):
                    messages.error(request, 'The appointment type selected is invalid.')
                    return render(request, 'core/edit_appointment.html', {'appointment': appointment, 'lead_data': lead, 'base_template': base_template, 'appointment_types': appointment_types})
                appointment.appointment_type = appointment_type
                
                property_id = request.POST.get('property_id')
                if property_id:
                    try:
                        property_id = int(property_id)
                        if property_id <= 0:
                            raise ValueError
                        appointment.property_id = property_id
                    except (ValueError, TypeError):
                        messages.error(request, 'The property ID provided is invalid.')
                        return render(request, 'core/edit_appointment.html', {'appointment': appointment, 'lead_data': lead, 'base_template': base_template, 'appointment_types': appointment_types})
                
                property_type = request.POST.get('property_type')
                if property_type:
                    if property_type not in ['Sale', 'Rent']:
                        messages.error(request, 'The property type provided is invalid.')
                        return render(request, 'core/edit_appointment.html', {'appointment': appointment, 'lead_data': lead, 'base_template': base_template, 'appointment_types': appointment_types})
                    appointment.property_type = property_type
                
                appointment.save()
                if request.user.role == 'company':
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Appointment Updated'
                    )
                messages.success(request, 'Appointment updated successfully.')
                return redirect('view-schedule', lead_id=appointment_uuid)
                
            except Exception:
                messages.error(request, 'Unable to update the appointment.')
        
        appointment_types = dict(APPOINTMENT_TYPE)
        
        context = {
            'appointment': appointment,
            'lead_data': lead,
            'base_template': base_template,
            'appointment_types': appointment_types,
        }
        
        return render(request, 'core/edit_appointment.html', context)
        
    except Appointments.DoesNotExist:
        messages.error(request, 'The requested appointment could not be found.')
        return redirect('appointment')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def view_client(request, appointment_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    user_role = request.user.role
    if user_role == 'company':
        base_template = 'company/base.html'
    elif user_role == 'agent':
        base_template = 'agent/base.html'
    else:
        base_template = 'estate/base.html'
    try:
        if request.user.role == 'company':
            company=CompanyInformation.objects.get(user= request.user)
            lead_item=LeadInfo.objects.filter(company_uuid=company.unique_company_id).first()
            if lead_item.company_uuid == company.unique_company_id:
                leads=LeadInfo.objects.filter(company_uuid=company.unique_company_id)
            else:
                messages.warning(request, 'Access denied: Unauthorized action.')
                return redirect('landing')
        elif request.user.role == 'agent':
            agent= AgentInformation.objects.get(user=request.user)
            lead_item= LeadInfo.objects.filter(agent_id=agent.agent_uuid).first()
            if lead_item.agent_id == agent.agent_uuid:
                leads= LeadInfo.objects.filter(agent_id=agent.agent_uuid)
            else:
                messages.warning(request, 'Access denied: Unauthorized action.')
                return redirect('landing')
        else:
            messages.info(request, 'Invalid Action')
            return redirect('landing')
        return render(request, 'core/lead_list.html', {'leads': leads, 'base_template': base_template, 'appointment_id':appointment_uuid})
    except ObjectDoesNotExist:
        messages.error(request, 'Data not found.')
        return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def add_client(request, lead_uuid, appointment_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        if request.user.role == 'company':
            company= CompanyInformation.objects.get(user=request.user)
            raw_data= Appointments.objects.get(appointment_uuid=appointment_uuid)
            raw_lead_data= LeadInfo.objects.get(lead_id=lead_uuid)
            if raw_data.company_uuid == company.unique_company_id and raw_lead_data.company_uuid == company.unique_company_id:
                appointment_data= raw_data
                lead_data= raw_lead_data
            else:
                messages.warning(request, 'Access denied: Unauthorized action.')
                return redirect('landing')
        elif request.user.role == 'agent':
            agent= AgentInformation.objects.get(user=request.user)
            raw_data= Appointments.objects.get(appointment_uuid=appointment_uuid)
            raw_lead_data= LeadInfo.objects.get(lead_id=lead_uuid)
            if raw_data.agent_uuid == agent.agent_uuid and raw_lead_data.agent_id == agent.agent_uuid:
                appointment_data=raw_data
                lead_data= raw_lead_data
            else:
                messages.warning(request, 'Access denied: Unauthorized action.')
                return redirect('landing')
        else:
            return redirect('landing')
        
        appointment_data.lead_uuid= lead_data.lead_id
        appointment_data.save()
        messages.success(request, 'Client successfully added to appointment.')
        return redirect('view-schedule', raw_data.appointment_uuid)
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
    
def delete_appointment(request, appointment_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        appointment=Appointments.objects.get(appointment_uuid=appointment_uuid)
        if request.user.role == 'company':
            try:
                company= CompanyInformation.objects.get(user=request.user)
                if appointment.company_uuid == company.unique_company_id:
                    appointment.delete()
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Appointment Deleted'
                    )
                    messages.success(request, 'Appointment deleted successfully.')
                    return redirect('appointment')
                else:
                    messages.error(request, 'Access denied: Unauthorized action.')
                    return redirect('landing')
            except ObjectDoesNotExist:
                messages.error(request, 'An unexpected error occurred.')
                return redirect('landing')
        elif request.user.role == 'agent':
            try:
                agent=AgentInformation.objects.get(user=request.user)
                if appointment.agent_uuid == agent.agent_uuid:
                    appointment.delete()
                    messages.success(request, 'Appointment deleted successfully.')
                    return redirect('appointment')
                else:
                    messages.error(request, 'Access denied: Unauthorized action.')
                    return redirect('landing')
            except ObjectDoesNotExist:
                messages.error(request, 'An unexpected error occurred.')
                return redirect('landing')
        else:
            messages.error(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def delete_client(request, appointment_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to continue.')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access denied: Unauthorized action.')
        return redirect('landing')
    try:
        appointment=Appointments.objects.get(appointment_uuid=appointment_uuid)
        if request.user.role == 'company':
            try:
                company= CompanyInformation.objects.get(user=request.user)
                if appointment.company_uuid == company.unique_company_id:
                    appointment.lead_uuid = None
                    appointment.save()
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Client Data Deleted'
                    )
                    messages.success(request, 'Client information removed from appointment.')
                    return redirect('view-schedule', appointment.appointment_uuid)
                else:
                    messages.error(request, 'Access denied: Unauthorized action.')
                    return redirect('landing')
            except ObjectDoesNotExist:
                messages.error(request, 'An unexpected error occurred.')
                return redirect('landing')
        elif request.user.role == 'agent':
            try:
                agent=AgentInformation.objects.get(user=request.user)
                if appointment.agent_uuid == agent.agent_uuid:
                    appointment.lead_uuid = None
                    appointment.save()
                    messages.success(request, 'Client information removed from appointment.')
                    return redirect('view-schedule', appointment_uuid)
                else:
                    messages.error(request, 'Access denied: Unauthorized action.')
                    return redirect('landing')
            except ObjectDoesNotExist:
                messages.error(request, 'An unexpected error occurred.')
                return redirect('landing')
        else:
            messages.error(request, 'Access denied: Unauthorized action.')
            return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})






def privacy_terms_sheet(request):
    return render(request, 'core/legal_privacy_sheet.html')

def partnership_terms(request):
    return render(request, 'core/partnership_terms.html')


def estate_web_guide(request):
    return render(request, 'core/faq.html')


def ratelimit_error(request, exception=None):
    return render(request, 'core/429.html', status=429)

def lockout_response(request, credentials, *args, **kwargs):
    return render(request, 'core/lockout.html', status=403)


