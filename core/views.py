from django.shortcuts import render, redirect
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


# Create your views here.
def landing_page(request):
    if not request.user.is_authenticated:
        return render(request, 'core/landing.html')
    else:
        if request.user.role == 'company':
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url if next_url else 'company:dashboard')
        elif request.user.role == 'agent':
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url if next_url else 'agent:dashboard')
        elif request.user.role == 'customer':
            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url if next_url else 'customer:user-profile')
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
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


'''New Multi-Channel Feedback System — receives AJAX POST from the feedback modal'''
@require_POST
def submit_feedback(request):
    try:
        reaction   = request.POST.get('reaction',  '').strip()
        category   = request.POST.get('category',  '').strip()
        details    = request.POST.get('details',   '').strip()
        role       = request.POST.get('role',      '').strip()
        screenshot = request.FILES.get('screenshot', None)

        if not reaction or not category:
            messages.error(request, 'Reaction and category are required.')
            return HttpResponse(status=400)

        try:
            reaction_int = int(reaction)
            if reaction_int not in range(1, 6):
                raise ValueError
        except ValueError:
            messages.error(request, 'Invalid reaction value.')
            return HttpResponse(status=400)

        valid_categories = ['bug', 'feature', 'complaint', 'praise']
        if category not in valid_categories:
            messages.error(request, 'Invalid category.')
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

        messages.success(request, 'Thanks for your feedback! We read every submission.')
        if 'HTTP_REFERER' in request.META:
            return redirect(request.META['HTTP_REFERER'])  
        else:
            messages.error(request, 'Error Redirecting')
            return redirect('landing')

    except Exception:
        print('[Feedback Error]')
        messages.error(request, 'Something went wrong. Please try again.')
        return HttpResponse(status=500)
'''Property Management'''

def sell_property(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login in required')
        return redirect('login')
 
    if request.user.role == 'customer':
        messages.info(request, 'Feature Coming Out Soon')
        return redirect('landing')
 
    try:
        user_role = request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template = 'estate/base.html'
            
        if request.user.role == 'agent':
            agent=AgentInformation.objects.get(user_id=request.user.id)
            company=get_agent_company(agent)
            
            allowed, reason= can_add_to_inventory(agent, company)
            if not allowed:
                messages.error(request, reason)
                return redirect('listings')
        elif request.user.role == 'company':
            """
            Company listed themselves
            """
            company=CompanyInformation.objects.get(user_id=request.user.id)
            agent=None
            allowed, reason= can_add_to_inventory(agent, company)
            if not allowed:
                messages.error(request, reason)
                return redirect('listings')
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
                        company = CompanyInformation.objects.get(user_id=request.user.id)
                        landlord.company_uuid  = company.unique_company_id
                        landlord.user_id       = request.user.id
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
                        agent = AgentInformation.objects.get(user_id=request.user.id)
                        landlord.agent_uuid   = str(agent.agent_uuid)
                        if agent.company_uuid:
                            landlord.company_uuid = agent.company_uuid
                        landlord.user_id= request.user.id
                        landlord.time_stamp= timezone.now()
                        landlord.is_listed=False
                        landlord.save()
 
                        image_form.instance = landlord
                        image_form.save()
 
                        # ── Initial scoring ──────────────────────────
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
        messages.info(request, 'Coming out soon')
        return redirect('landing')
 
    try:
        submitted  = False
        user_role  = request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template = 'estate/base.html'
        if request.user.role == 'agent':
            agent=AgentInformation.objects.get(user_id=request.user.id)
            company=get_agent_company(agent)
            
            allowed, reason= can_add_to_inventory(agent, company)
            if not allowed:
                messages.error(request, reason)
                return redirect('listings')
        elif request.user.role == 'company':
            """
            Company listed themselves
            """
            company=CompanyInformation.objects.get(user_id=request.user.id)
            agent=None
            allowed, reason= can_add_to_inventory(agent, company)
            if not allowed:
                messages.error(request, reason)
                return redirect('listings')
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
                        company = CompanyInformation.objects.get(user_id=request.user.id)
                        landlord.company_uuid  = company.unique_company_id
                        landlord.user_id       = request.user.id
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
                        agent = AgentInformation.objects.get(user_id=request.user.id)
                        landlord.agent_uuid = agent.agent_uuid
                        if agent.company_uuid is not None:
                            landlord.company_uuid = agent.company_uuid
                        landlord.user_id      = request.user.id
                        landlord.time_stamp   = timezone.now()
                        landlord.is_listed=False
                        landlord.save()
 
                        image_form.instance = landlord
                        image_form.save()
 
                        # ── Initial scoring ──────────────────────────
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


def toggle_listing(request, property_id, property_type):
    """
    Toggles a property between inventory (private) and listed(public).
    Supports AJAX
    """
    is_ajax=request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    Model=PropertyManagementSale if property_type == 'sale' else PropertyManagementRent
    #FIXME you can only toggle listings the company account listed  
    try:
        prop=Model.objects.get(pk=property_id, user_id=request.user.id)
    except:
        if is_ajax:
            return JsonResponse({'error':'Not found'}, status=404)
        messages.error(request, 'Property not found')
        return redirect('listings')

    if prop.is_listed:
        prop.is_listed=False
        prop.save(update_fields=['is_listed'])
        msg='Property moved back to inventory.'
        if is_ajax:
            return JsonResponse({'is_lited': False, 'message':msg})
        messages.success(request, msg)
    else:
        if request.user.role == 'agent':
            agent=AgentInformation.objects.get(user_id=request.user.id)
            company=get_agent_company(agent)
        elif request.user.role == 'company':
            agent=None
            company=CompanyInformation.objects.get(user_id=request.user.id)
        
        allowed,reason= can_go_live(agent, company)
        if not allowed:
            if is_ajax:
                return JsonResponse({'error': reason}, status=403)
            messages.error(request, reason)
            return redirect('listings')
        prop.is_listed=True
        prop.save(update_fields=['is_listed'])
        msg= 'Property is now live on the platform.'
        if is_ajax:
            return JsonResponse({'is_listed':True, 'message': msg})
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
    if not request.user.is_authenticated:
        messages.info(request, 'Login required')
        return redirect('landing')
    if not request.user.role == 'customer':
        messages.info(request, 'Coming out soon')
        return redirect('landing')
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
        if property.user_id != request.user.id:
            messages.warning(request, 'ACCESS DENIED')
            return redirect('landing')
        prop_form= LeaseForm(request.POST or None,request.FILES or None, instance=property)
        image_form = RentImageFormSet(request.POST or None, request.FILES or None, instance=property)
        company=CompanyInformation.objects.get(user_id=request.user.id)
        if prop_form.is_valid() and image_form.is_valid():
            prop_form.save()
            image_form.save()
            messages.success(request, "Property Updated Successfully")
            CompanyActivityLog.objects.create(
                company=company,
                action= 'Property Listing Updated'
            )
            return redirect('listings')
        return render(request, 'core/update_property.html', {'property': property, 'form': prop_form, 'images': image_form, 'base_template':base_template})
        
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


#view to update listed property on rent
def update_property_sale(request, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.info(request, 'Coming out soon')
        return redirect('landing')
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
        if property.user_id != request.user.id:
            messages.warning(request, 'ACCESS DENIED')
            return redirect('landing')
        prop_form= SellForm(request.POST or None, request.FILES or None, instance=property)
        image_form = SaleImageFormSet(request.POST or None, request.FILES or None, instance=property)
        company=CompanyInformation.objects.get(user_id=request.user.id)
        if prop_form.is_valid() and image_form.is_valid():
            prop_form.save()
            image_form.save()
            messages.success(request, "Property Updated Successfully")
            CompanyActivityLog.objects.create(
                company=company,
                action= 'Property Listing Updated'
            )
            return redirect('listings')
        return render(request, 'core/update_property_s.html', {'property': property, 'form': prop_form,'images': image_form, 'base_template':base_template})
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


#view to delete listings
def delete_property_on_lease(request, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)
        #deleting using th property id
        property1= PropertyManagementRent.objects.get(pk=property_id)
        #protects against other user deleting ones property
        if request.user.id != property1.user_id:
            messages.warning(request, 'ACCESS DENIED')
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
            messages.success(request, ("Property deleted successfully"))
            CompanyActivityLog.objects.create(
                company=company,
                action= 'Property Listing Deleted'
            )
            return redirect('listings')
        except Exception:
            messages.error(request, 'An error occured.....')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})

#view to delete listings
def delete_property_on_sale(request, property_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.warning(request, 'Access Denied')
        return redirect('landing')
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)
        property1= PropertyManagementSale.objects.get(pk=property_id)
        
        #Additional layer of security
        if request.user.id != property1.user_id:
            messages.warning(request, 'Access Denied')
            return redirect()
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
        messages.success(request, ("Property deleted successfully"))
        CompanyActivityLog.objects.create(
            company=company,
            action= 'Property Listing Deleted'
        )
        return redirect('listings')
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
            # save() with commit=False gives us the instance without writing
            # M2M yet — we need to call save_m2m() after saving the instance
            partnership = form.save(commit=False)
            partnership.save()           # writes the main row to the database
            form.save_m2m()              # now writes the M2M (property_types, partnership_benefits)

            messages.success(
                request,
                "Thank you for applying! Our partnerships team will review your application "
                "and reach out within 3–5 business days."
            )
            return redirect('partner-success')   # change this URL name to match your urls.py

        else:
            # Form has errors — re-render with the same POST data so the user
            # doesn't have to retype everything
            messages.error(
                request,
                "Please correct the errors below and resubmit your application."
            )

    else:
        form = PartnershipForm()

    return render(request, 'core/partner.html', {'form': form})


def partner_success(request):
    """Simple success page after a partnership application is submitted."""
    return render(request, 'core/partner_success.html')



def appointment_detail(request,appt_uuid):
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
            sample= Appointments.objects.get(appointment_uuid=appt_uuid)
            if company.unique_company_id != sample.company_uuid:
                messages.warning(request, 'Unauthorized Access')
                return redirect('appointment')
            appointment=sample
        else:
            agent=AgentInformation.objects.get(user_id=request.user.id)
            sample= Appointments.objects.get(appointment_uuid=appt_uuid)
            if agent.agent_uuid != sample.agent_uuid:
                messages.warning(request, 'Unauthorized Access')
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
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Appointment Created'
                    )
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
        
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


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
            return render(request, 'core/appointment.html', {'appointments': total_appointment,'base_template':base_template ,'agent_name':f'{agent.first_name} {agent.last_name}'})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def estate_blog(request):
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
        return render(request, 'core/estate_blog.html', {'base_template': base_template})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def manage_listings(request):
    if not request.user.is_authenticated:
        messages.info(request, 'login required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.warning(request, 'Access Restricted')
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
            agent=None
            property_on_lease=PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
            property_on_sale=PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
            role='company'
        elif request.user.role == 'agent':
            agent=AgentInformation.objects.get(user_id=request.user.id)
            company=None
            if agent.company_uuid:
                company=CompanyInformation.objects.get(unique_company_id=agent.company_uuid)
            property_on_lease=PropertyManagementRent.objects.filter(agent_uuid=agent.agent_uuid)
            property_on_sale=PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid)
            role='agent'
        else:
            messages.error(request, 'An error occured')
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
            item= Appointments.objects.filter(company_uuid=company.unique_company_id).get(appointment_uuid=appointment_uuid)
            CompanyActivityLog.objects.create(
                company=company,
                action= 'Appointment Updated'
            )
            if item.company_uuid == company.unique_company_id:
                appointment=item
            else:
                messages.warning(request, 'Access Denied')
                return redirect('landing')
        else:
            agent = AgentInformation.objects.get(user_id=request.user.id)
            item = Appointments.objects.filter(agent_uuid=agent.agent_uuid).get(appointment_uuid=appointment_uuid)
            if item.agent_uuid == agent.agent_uuid:
                appointment= item
            else:
                messages.warning(request, 'Access Denied')
                return redirect('landing')
            
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
                return redirect('view-schedule', lead_id=appointment_uuid)
                
            except Exception:
                messages.error(request, 'Error updating appointment')
        
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
        return redirect('appointment')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



def view_client(request, appointment_uuid):
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
            lead_item=LeadInfo.objects.filter(company_uuid=company.unique_company_id).first()
            if lead_item.company_uuid == company.unique_company_id:
                leads=LeadInfo.objects.filter(company_uuid=company.unique_company_id)
            else:
                messages.warning(request, 'Access Denied')
                return redirect('landing')
        except:
            agent= AgentInformation.objects.get(user_id=request.user.id)
            lead_item= LeadInfo.objects.filter(agent_id=agent.agent_uuid).first()
            if lead_item.agent_id == agent.agent_uuid:
                leads= LeadInfo.objects.filter(agent_id=agent.agent_uuid)
            else:
                messages.warning(request, 'Access Denied')
                return redirect('landing')
        return render(request, 'core/lead_list.html', {'leads': leads, 'base_template': base_template, 'appointment_id':appointment_uuid})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def add_client(request, lead_uuid, appointment_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        if request.user.role == 'company':
            company= CompanyInformation.objects.get(user_id=request.user.id)
            raw_data= Appointments.objects.get(appointment_uuid=appointment_uuid)
            raw_lead_data= LeadInfo.objects.get(lead_id=lead_uuid)
            if raw_data.company_uuid == company.unique_company_id and raw_lead_data.company_uuid == company.unique_company_id:
                appointment_data= raw_data
                lead_data= raw_lead_data
            else:
                messages.warning(request, 'Restricted Action')
                return redirect('landing')
        elif request.user.role == 'agent':
            agent= AgentInformation.objects.get(user_id=request.user.id)
            raw_data= Appointments.objects.get(appointment_uuid=appointment_uuid)
            raw_lead_data= LeadInfo.objects.get(lead_id=lead_uuid)
            if raw_data.agent_uuid == agent.agent_uuid and raw_lead_data.agent_id == agent.agent_uuid:
                appointment_data=raw_data
                lead_data= raw_lead_data
            else:
                messages.warning(request, 'Restricted Action')
                return redirect('landing')
        else:
            return redirect('landing')
        
        appointment_data.lead_uuid= lead_data.lead_id
        appointment_data.save()
        messages.success(request, 'Client Added')
        return redirect('view-schedule', raw_data.appointment_uuid)
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})
    
def delete_appointment(request, appointment_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        appointment=Appointments.objects.get(appointment_uuid=appointment_uuid)
        if request.user.role == 'company':
            try:
                company= CompanyInformation.objects.get(user_id=request.user.id)
                if appointment.company_uuid == company.unique_company_id:
                    appointment.delete()
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Appointment Deleted'
                    )
                    messages.success(request, 'Appointment Deleted')
                    return redirect('appointment')
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
                    appointment.delete()
                    messages.success(request, 'Appointment Deleted')
                    return redirect('appointment')
                else:
                    messages.error(request, 'Access Denied')
                    return redirect('landing')
            except ObjectDoesNotExist:
                messages.error(request, 'An error occured')
                return redirect('landing')
        else:
            messages.error(request, 'Access Denied')
            return redirect('landing')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})


def delete_client(request, appointment_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role == 'customer':
        messages.error(request, 'Access Denied')
        return redirect('landing')
    try:
        appointment=Appointments.objects.get(appointment_uuid=appointment_uuid)
        if request.user.role == 'company':
            try:
                company= CompanyInformation.objects.get(user_id=request.user.id)
                if appointment.company_uuid == company.unique_company_id:
                    appointment.lead_uuid = None
                    appointment.save()
                    CompanyActivityLog.objects.create(
                        company=company,
                        action= 'Client Data Deleted'
                    )
                    messages.success(request, 'Client Info Removed')
                    return redirect('view-schedule', appointment.appointment_uuid)
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
                    return redirect('view-schedule', appointment_uuid)
                else:
                    messages.error(request, 'Access Denied')
                    return redirect('landing')
            except ObjectDoesNotExist:
                messages.error(request, 'An error occured')
                return redirect('landing')
        else:
            messages.error(request, 'Access Denied')
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

