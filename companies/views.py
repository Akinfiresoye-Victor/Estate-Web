from django.shortcuts import render, redirect
from .forms import SocialLinksFormset, CompanyForm
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import CompanyInformation, CompanyAnalytics, SessionId
from members.views import logout_user
from core.models import PropertyManagementRent, PropertyManagementSale
from estate.models import LeadInfo
from members.models import User
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator



#Companies dashboard
def dashboard(request):
    try:
        if not request.user.is_authenticated:
            messages.info(request, 'You must be authenticated to access this page')
            return redirect('landing')
        if not request.user.role == 'company':
            messages.info(request, 'Account must be a company account')
            return redirect('landing')
        try:
            company = CompanyInformation.objects.get(user_id=request.user.id) 
            social_links = company.social.all()
            total_views_raw= company.analytics.all()
            if total_views_raw:
                for views in total_views_raw:
                    profile_views = views.profile_views
            else:
                profile_views = 0
            
            total_prop= PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id).count() + PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id).count()
            total_inq=LeadInfo.objects.filter(company_uuid=company.unique_company_id).count()
            context = {
                'company': company,
                'social_links': social_links,
                'total_properties': total_prop,
                'total_views': profile_views,
                'total_inquiries': total_inq,
                'average_rating': 0.0,
                'recent_activities': 'None',
                'recent_activities': 'None' 
            }
            print('working here')
            return render(request, 'company/dashboard.html', context)
            
        except CompanyInformation.DoesNotExist:
            messages.warning(request, 'Company Profile has to be setup to access other pages')
            return redirect('company:company_form')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})



#form all companies must fill before they access the dashboard
def company_form(request):
    if request.user.is_authenticated:
        if not request.user.role == 'company':
            messages.info(request, 'Account must be a company account')
            return redirect('landing')
        try:
            submitted=False
            if request.method == 'POST':
                try:
                    if CompanyInformation.objects.get(user_id=request.user.id):
                        return redirect('company:dashboard')
                except CompanyInformation.DoesNotExist:
                    comp_form=CompanyForm(request.POST or None, request.FILES or None)
                    link_form=SocialLinksFormset(request.POST or None)
                    with transaction.atomic():
                        if comp_form.is_valid() and link_form.is_valid():
                            company_form=comp_form.save(commit=False)
                            company_form.user_id= request.user.id
                            User.email= company_form.email
                            company_form.save()
                            link_form.instance=company_form
                            link_form.save()
                            messages.success(request, 'Company Profile Successfully Set')
                            return HttpResponseRedirect('?submitted=True')
            else:
                comp_form= CompanyForm()
                link_form= SocialLinksFormset()
                if 'submitted' in request.GET:
                    submitted=True
            return render(request, 'company/company_form.html', {
                                                                    'form': comp_form,
                                                                    'social': link_form,
                                                                    'submitted': submitted
                        })
            
            
        except Exception as e:
            print(f'Error is {e}')
            return render(request, 'estate/error_page.html', {'e': e}, {'e':e})
    else:
        messages.info(request, 'open a company account to perform this action')
        return redirect('articles')

def update_company_profile(request, company_id):
    if request.user.is_authenticated:
        
        try:
            company_information=CompanyInformation.objects.get(pk=company_id)
            if request.user.id == company_information.user_id:
                if request.method == 'POST':
                    comp_form = CompanyForm(request.POST, request.FILES, instance=company_information)
                    link_form = SocialLinksFormset(request.POST, request.FILES, instance=company_information)
                    if comp_form.is_valid() and link_form.is_valid():
                        with transaction.atomic():
                            company = comp_form.save(commit=False)
                            company.user_id = request.user.id
                            company.save()
                            link_form.save()
                            messages.success(request, 'Profile Updated Successfully')
                            return redirect('company:dashboard')
                else:
                    comp_form = CompanyForm(instance=company_information)
                    link_form = SocialLinksFormset(instance=company_information)
                return render(request, 'company/update_company_profile.html', {
                    'form':comp_form,
                    'social': link_form
                })
            else:
                messages.warning(request, 'Youre not authorized to visit that page please relogin and be careful!!')
                logout_user(request)
        except Exception as e:
            print(f'Error is {e}')
            return render(request, 'estate/error_page.html', {'e': e})
    else:
        messages.success(request, 'You have to be logged in to access this page')
        return redirect('login')


def manaage_listings(request):
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)
        company_uuid=company.unique_company_id
        property_on_lease=PropertyManagementRent.objects.filter(company_uuid=company_uuid)
        property_on_sale=PropertyManagementSale.objects.filter(company_uuid=company_uuid)
        return render(request, 'company/company_listings.html', {'on_lease':property_on_lease,
                                                        'on_sale':property_on_sale})
    except Exception as e:
        print(e)
        return render(request, 'estate/error_page.html', {'e':e})


def company_analytics(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'You must be logged in to access this page.')
        return redirect('login')
        
    if request.user.role != 'company':
        messages.info(request, 'You must open a company account to perform this action.')
        return redirect('landing')

    try:
        messages.info(request, 'Numbers might seem low since we just launched')
        company = CompanyInformation.objects.get(user_id=request.user.id)

        try:
            analytics = company.analytics.get()
        except ObjectDoesNotExist:
            analytics = CompanyAnalytics.objects.create(
                company=company,
                profile_views=0, 
                property_views_l=0,
                property_views_s=0,
                last_month_profile_views=0,
                last_month_lease_views=0,
                last_month_sale_views=0,
            )

                # --- View Calculation Logic ---
        time_since_reset = timezone.now() - analytics.last_reset_date
        days_since_reset = time_since_reset.days # total_seconds() / 86400
        
        # 2. Check if 30 days have passed
        if days_since_reset >= 30:
            # A. Reset the views to 0
            analytics.last_month_profile_views= analytics.profile_views
            analytics.last_month_lease_views=analytics.property_views_l
            analytics.last_month_sale_views=analytics.property_views_s
            analytics.profile_views = 0 
            analytics.property_views_l=0
            analytics.property_views_s=0
            
            session_id=SessionId.objects.all()
            session_id.delete()
            
            # B. UPDATE the last_reset_date to today
            analytics.last_reset_date = timezone.now()
            
            # C. Save the changes to the database
            analytics.save()
            
        profile_views = analytics.profile_views
        total_prop_views = analytics.property_views_l + analytics.property_views_s
        prop_views_on_sale = analytics.property_views_s
        prop_views_on_lease = analytics.property_views_l
        
        
        if analytics.last_month_lease_views == 0 and analytics.property_views_l == 0:
            monthly_lease_view_incr= 0
            
        
        elif analytics.last_month_lease_views == 0:
            monthly_lease_view_incr= 100

        elif analytics.last_month_lease_views > analytics.property_views_l:
            # CORRECTED: Denominator changed to last_month_lease_views
            if analytics.last_month_lease_views == 0: # Already handled above, but for safety
                monthly_lease_view_incr = 0
            else:
                monthly_lease_view_incr= -(analytics.last_month_lease_views - analytics.property_views_l )/analytics.last_month_lease_views * 100
            
        else:
            monthly_lease_view_incr= (analytics.property_views_l - analytics.last_month_lease_views )/analytics.last_month_lease_views * 100
        
        
        # --- Profile Views: CORRECTED LOGIC REMAINS ---
        if analytics.last_month_profile_views == 0 and profile_views == 0:
            monthly_profile_view_incr = 0
            
        elif analytics.last_month_profile_views == 0:
            monthly_profile_view_incr = 100
            
        elif analytics.last_month_profile_views > profile_views:
            # Denominator is last_month_profile_views
            monthly_profile_view_incr = -(analytics.last_month_profile_views - profile_views) / analytics.last_month_profile_views * 100 
            
        else:
            # Denominator is last_month_profile_views
            monthly_profile_view_incr = (profile_views - analytics.last_month_profile_views) / analytics.last_month_profile_views * 100
        
        # --- Sale Views: CORRECTED LOGIC REMAINS ---
        if analytics.last_month_sale_views == 0 and analytics.property_views_s == 0:
            monthly_sale_view_incr = 0
        
        elif analytics.last_month_sale_views == 0:
            monthly_sale_view_incr = 100
            
        elif analytics.last_month_sale_views > analytics.property_views_s :
            # Denominator is last_month_sale_views
            monthly_sale_view_incr = -(analytics.last_month_sale_views - analytics.property_views_s) / analytics.last_month_sale_views * 100 
            
        else:
            # Denominator is last_month_sale_views
            monthly_sale_view_incr = (analytics.property_views_s - analytics.last_month_sale_views) / analytics.last_month_sale_views * 100
        
        total_prop_incr_perc= monthly_sale_view_incr + monthly_lease_view_incr/2


        
        '''Competitions'''
        companies= CompanyInformation.objects.all()
        total_companies_eng=[]
        total_company_listings_views= analytics.property_views_s + analytics.property_views_l
        
        
        prop_rent=PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
        prop_sale=PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
        
        wishlist_rent_list=[]
        wishlist_sale_list=[]
        for on_lease in prop_rent:
            count=on_lease.total_likes
            wishlist_rent_list.append(count)
        for on_sale in prop_sale:
            count=on_sale.total_likes
            wishlist_sale_list.append(count)
            
        wishlist_rent = sum(wishlist_rent_list)
        wishlist_sale = sum(wishlist_sale_list)
        total_liked_prop= wishlist_rent + wishlist_sale
        eng_rate=engagement_rate(total_liked_prop,total_company_listings_views, profile_views)
        analytics.competition=eng_rate
        analytics.save()
        
        
        for comp in companies:
            prop_rent=PropertyManagementRent.objects.filter(company_uuid=comp.unique_company_id)
            prop_sale=PropertyManagementSale.objects.filter(company_uuid=comp.unique_company_id)
            wishlist_rent_list=[]
            wishlist_sale_list=[]
            for on_lease in prop_rent:
                count=on_lease.total_likes
                wishlist_rent_list.append(count)
            for on_sale in prop_sale:
                count=on_sale.total_likes
                wishlist_sale_list.append(count)
                
            wishlist_rent = sum(wishlist_rent_list)
            wishlist_sale = sum(wishlist_sale_list)
            total_liked_prop= wishlist_rent + wishlist_sale
            
            try:
                analy = comp.analytics.get()
            except ObjectDoesNotExist:
                analy = CompanyAnalytics.objects.create(
                    company=comp,
                    profile_views=0, 
                    property_views_l=0,
                    property_views_s=0,
                    last_month_profile_views=0,
                    last_month_lease_views=0,
                    last_month_sale_views=0,
                )

            total_company_listings_views= analy.property_views_s + analy.property_views_l
            eng_rate=engagement_rate(total_liked_prop,total_company_listings_views, analy.profile_views)
            
            # This is the correct line to build the list for competition calculation
            total_companies_eng.append(eng_rate)
            
        # 1. Calculate competition score (now safe from ZeroDivisionError)
        total_eng_sum = sum(total_companies_eng)
        
        if total_eng_sum > 0:
            competition = (analytics.competition / total_eng_sum) * 100
        else:
            competition = 0
            
        # 2. Calculate Inquiry Conversion Rate (must be calculated after competition)
        total_inq=LeadInfo.objects.filter(company_uuid=company.unique_company_id).count()
        
        # Check for zero property views before division (Now safe)
        if total_prop_views > 0:
            inq_conv_rate=(total_inq/total_prop_views) * 100
        else:
            inq_conv_rate = 0
        
        # REMOVED: The final line 'inq_conv_rate=(total_inq/total_prop_views) *100' was deleted.
        
        # 3. Render the correct template
        return render(request, 'company/company_analytics.html', {
            'profile_views': profile_views,
            'prop_views': total_prop_views,
            'leased_view': prop_views_on_lease,
            'sale_view': prop_views_on_sale,
            'profile_incr_perc': monthly_profile_view_incr,
            'lease_incr_perc': monthly_lease_view_incr,
            'sale_incr_perc': monthly_sale_view_incr,
            'total_prop_incr_perc': total_prop_incr_perc,
            'engagement_rate': analytics.competition,
            'competition':competition,
            'inq_rate':inq_conv_rate
        })
        
    except CompanyInformation.DoesNotExist:
        messages.error(request, "Company profile not found.")
        return redirect('landing') # Redirect to a safe page if profile is missing
        
    except Exception as e:
        # Catch any unexpected errors (database connection, misconfigured settings, etc.)
        return render(request, 'estate/error_page.html', {'e': str(e)})


def appointment(request):
    return render(request, 'company/appointment.html', {})

def documents(request):
    return render(request, 'company/documents.html', {})

def reports(request):
    pass

def company_settings(request):
    return render(request, 'company/company_settings.html')


def lead_management(request):
    try:
        if not request.user.is_authenticated:
            messages.info(request, 'You have to be logged in to access this page')
            return redirect('landing')
        if not request.user.role == 'company':
            messages.info(request, 'You have to open a company account to access this page')
            return redirect('landing')
        company_uuid=CompanyInformation.objects.get(user_id=request.user.id).unique_company_id    
        general_leads=LeadInfo.objects.filter(company_uuid=company_uuid)
        p=Paginator(general_leads.order_by('-date_created'), 10)
        page=request.GET.get('page')
        leads=p.get_page(page)
        nums="a" * leads.paginator.num_pages
        lead_count=general_leads.count()
        new_leads=general_leads.filter(date_created=date.today()).count()
        
        
        '''Lead Stages'''
        potential_friend=general_leads.filter(stages='Potential Friend')
        true_friend=general_leads.filter(stages='True Friend')
        contracted=general_leads.filter(stages='Contracted')
        closed=general_leads.filter(stages='Closed/Won')
        disposition=general_leads.filter(stages='Disposition')
        new_lead_stage=general_leads.filter(stages='New')
        
        '''Lead Status'''
        contacted=general_leads.filter(status='Contacted')
        not_contacted=general_leads.filter(status= 'Not Contacted')
        attempt_contact=general_leads.filter(status= 'Contact Attempt')
        cold_lead= general_leads.filter(status= 'Cold Lead')
        warm_lead=general_leads.filter(status= 'Warm Lead')
        hot_lead=general_leads.filter(status= 'Hot Lead')
        qualified=general_leads.filter(status= 'Qualified')
        unqualified=general_leads.filter(status= 'Unqualified')




        context= {'lead_count':lead_count, 'new_leads': new_leads, 'leads':leads,'potential':potential_friend,
                    'potential_count': potential_friend.count(),'true_friend': true_friend,'true_friend_count':true_friend.count(),
                    'contracted':contracted,'contracted_count':contracted.count(),'closed':closed,'closed_count':closed.count(),
                    'disposition': disposition, 'disposition_count':disposition.count(), 'contacted':contacted, 'not_contacted':not_contacted,
                    'attempt':attempt_contact, 'cold_lead':cold_lead, 'warm_lead':warm_lead, 'hot_lead':hot_lead,
                    'qulified':qualified, 'unqualified':unqualified, 'nums': nums, 'new_stage':new_lead_stage.count()}
        return render(request, 'company/lead_management.html', context)
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})


def lead_detail(request, lead_id):
    client=LeadInfo.objects.get(pk=lead_id)
    if client.property_type =='Sale' :
        property=PropertyManagementSale.objects.get(pk=client.property_intrested)
    else:
        property=PropertyManagementRent.objects.get(pk=client.property_intrested)
    return render(request, 'company/lead_detail_page.html', {'lead':client, 'property':property})




def delete_lead(request, lead_id):
    if not request.user.is_authenticated and request.user.role == 'company':
        return redirect('landing')
    try:
        company= CompanyInformation.objects.get(user_id=request.user.id)
        lead_to_delete=LeadInfo.objects.get(pk=lead_id)
        if company.unique_company_id == lead_to_delete.company_uuid:
            lead_to_delete.delete()
            messages.success(request, "Client's Data Deleted Successfully")
            return redirect('company:lead-management')
        else:
            messages.warning(request, "You aren't authorized to perform that action")
            return redirect('landing')
    except Exception as e:
        return render(request, 'estate/error_page', {e})



@require_POST
def update_lead_status(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'You have to be authenticated to perform this action')
        return redirect('landing')
    if request.user.role !='company':
        messages.info(request, 'Access Denied')
        return redirect('landing')
    try:
        try:
            lead=LeadInfo.objects.get(pk=lead_id)
            new_status= request.POST.get('new_status')
            if not new_status:
                messages.error(request, 'Status Missing')
                return redirect('company:lead-management')
            lead.status=new_status
            lead.date_updated=timezone.now()
            lead.save()
            messages.success(request, 'Status Updated Successfully')
            return redirect('company:lead-detail', lead_id=lead_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Lead Not found <404>')
            return redirect('company:lead-management')
    except Exception as e:
        return render(request, 'estate/error_page.html')



@require_POST
def update_lead_stage(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'You have to be authenticated to perform this action')
        return redirect('landing')
    if request.user.role != 'company':
        messages.info(request, 'Access Denied')
        return redirect('landing')
    try:
        try:
            lead = LeadInfo.objects.get(pk=lead_id)
            new_stage = request.POST.get('new_stage')
            if not new_stage:
                messages.error(request, 'Stage Missing')
                return redirect('company:lead-management')
            lead.stages = new_stage
            lead.date_updated=timezone.now()
            lead.save()
            messages.success(request, 'Stage Updated Successfully')
            return redirect('company:lead-detail', lead_id=lead_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Lead Not found <404>')
            return redirect('company:lead-management')
    except Exception as e:
        return render(request, 'estate/error_page.html')


def company_profile(request, company_uuid):
    if request.user.is_authenticated:
        try:
            company = CompanyInformation.objects.get(unique_company_id=company_uuid)
            total_property_on_lease = PropertyManagementRent.objects.filter(company_uuid=company_uuid).count()
            total_property_on_sale = PropertyManagementSale.objects.filter(company_uuid=company_uuid).count()
            total_properties = int(total_property_on_lease) + int(total_property_on_sale)
            social_links = company.social.all()
            
            # Get querysets
            on_sale_qs = PropertyManagementSale.objects.filter(company_uuid=company_uuid)
            on_lease_qs = PropertyManagementRent.objects.filter(company_uuid=company_uuid)
            
            # Create paginators (4 items per page)
            p_sale = Paginator(on_sale_qs, 2)
            p_lease = Paginator(on_lease_qs, 2)
            
            # Get separate page numbers for each type
            page_sale = request.GET.get('page_sale', 1)
            page_rent = request.GET.get('page_rent', 1)
            
            properties_on_sale = p_sale.get_page(page_sale)
            properties_on_lease = p_lease.get_page(page_rent)
            
            try:
                prop_analytics=company.session_id.get(session_id=request.user.id)
            except ObjectDoesNotExist:
                prop_analytics=SessionId.objects.create(
                    company= company,
                    session_id=request.user.id,
                    inquires_check=0
                )
                profile= company.analytics.get()
                profile.profile_views +=1
                profile.save()
            
            return render(request, 'company/company_profile.html', {
                'company': company,
                'total_properties': total_properties,
                'properties_for_sale': total_property_on_sale,
                'properties_for_rent': total_property_on_lease,
                'social_links': social_links,
                'on_lease': properties_on_lease,
                'on_sale': properties_on_sale,
            })
        except Exception as e:
            return render(request, 'estate/error_page.html', {'e': e})


def properties_by_company(request, company_uuid):
    if request.user.is_authenticated:
        if request.user.role == 'company':
            messages.info(request, 'This page is for clients only')
            return redirect('company:dashboard')
        company=CompanyInformation.objects.get(unique_company_id=company_uuid)
        on_lease=PropertyManagementRent.objects.filter(company_uuid=company_uuid)
        on_sale=PropertyManagementSale.objects.filter(company_uuid=company_uuid)
        return render(request, 'company/company_properties.html', {
            'on_lease': on_lease,
            'on_sale': on_sale,
            'company':company
        })
        



def engagement_rate(total_liked_prop,total_company_listings_views, profile_views):
    total_engagements= total_liked_prop + total_company_listings_views + profile_views 
    engagement_rate=(total_engagements/User.objects.count()) * 100
    return engagement_rate
