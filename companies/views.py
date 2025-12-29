from django.shortcuts import render, redirect
from .forms import SocialLinksFormset, CompanyForm
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import CompanyInformation, CompanyAnalytics, SessionId, CompanyRating
from members.views import logout_user
from core.models import PropertyManagementRent, PropertyManagementSale, PropertyViews, Appointments
from estate.models import LeadInfo
from members.models import User
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404




def monthly_change(present_data, last_month_data):
    if last_month_data == 0 and present_data == 0:
        change=0
    elif last_month_data == 0:
        change=100
    elif last_month_data > present_data:
        change= -(last_month_data - present_data)/ last_month_data * 100
    else:
        change=(present_data - last_month_data)/ last_month_data * 100
    return change


def engagement_rate(total_liked_prop,total_company_listings_views, profile_views):
    total_engagements= total_liked_prop + total_company_listings_views + profile_views 
    engagement_rate=(total_engagements/User.objects.count()) * 100
    return engagement_rate


def get_total_likes(property_type, properties):
    if property_type == "Rent":
        rent_likes=[]
        for likes in properties:
            count=likes.total_likes
            rent_likes.append(count)
        total_likes=sum(rent_likes)
    elif property_type == "Sale":
        sale_likes=[]
        for likes in properties:
            count=likes.total_likes
            sale_likes.append(count)
        total_likes=sum(sale_likes)
    else:
        total_likes=0
    return total_likes


def total_companies_engagement_calculator(total_rate, personal_rate, personal_uuid, property_views):
    if total_rate > 0:
        total_company_competition=(personal_rate / total_rate) * 100
    else:
        total_company_competition = 0

    total_impression=LeadInfo.objects.filter(company_uuid=personal_uuid).count()
    
    if property_views > 0:
        expression_rate=(total_impression/property_views) * 100
    else:
        expression_rate= 0
    return [total_company_competition, expression_rate]



def reset_button(general_data):
    time_since_reset= timezone.now() - general_data.last_reset_date
    days_since_reset=time_since_reset.days
    
    if days_since_reset >=30:
        general_data.last_month_profile_views = general_data.profile_views
        general_data.last_month_lease_views = general_data.property_views_l
        general_data.last_month_sale_views= general_data.property_views_s
        
        general_data.profile_views = 0
        general_data.property_views_l = 0
        general_data.property_views_s=0
        
        session_id=SessionId.objects.all()
        session_id.delete()
        
        general_data.last_reset_date = timezone.now()
        
        general_data.save()



def property_views_count(property_type, property_id, reset):
    if property_type == "Rent":
        property_to_be_checked=PropertyViews.objects.filter(property_type='Rent', property_id=property_id)
    else:
        property_to_be_checked=PropertyViews.objects.filter(property_type='Sale', property_id=property_id)
    
    if property_to_be_checked.exists():
        x=0
        for prop in property_to_be_checked:
            x+=1
            if reset:
                prop.delete()
                result=0
            else:
                result=x
    else:
        result=0
    return result






#Companies dashboard
def dashboard(request):
    try:
        if not request.user.is_authenticated:
            messages.info(request, 'log in to access page')
            return redirect('landing')
        if not request.user.role == 'company':
            messages.info(request, 'Company account only')
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
            reviews = CompanyRating.objects.filter(company_uuid=company.unique_company_id).select_related('user')
            rating_data = reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
            )

            average_rating = rating_data['avg_rating'] or 0.0
            total_reviews = rating_data['total_reviews']

            context = {
                'company': company,
                'social_links': social_links,
                'total_properties': total_prop,
                'total_views': profile_views,
                'total_inquiries': total_inq,
                'average_rating': average_rating,
            }
            print('working here')
            return render(request, 'company/dashboard.html', context)
            
        except CompanyInformation.DoesNotExist:
            messages.warning(request, 'Set company profile')
            return redirect('company:company_form')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})



#form all companies must fill before they access the dashboard
def company_form(request):
    if request.user.is_authenticated:
        if not request.user.role == 'company':
            messages.info(request, 'Company account only')
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
                            messages.success(request, 'Profile Successfully Set')
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
        messages.info(request, 'Company account only')
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
                messages.warning(request, 'Access Denied')
                logout_user(request)
        except Exception as e:
            print(f'Error is {e}')
            return render(request, 'estate/error_page.html', {'e': e})
    else:
        messages.success(request, 'Log in to gain access')
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
        messages.warning(request, 'login Required')
        return redirect('login')
        
    if request.user.role != 'company':
        messages.info(request, 'Company account only')
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

        reset_button(analytics)
        profile_views = analytics.profile_views
        companies_properties_lease=PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
        companies_properties_sale=PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
        each_lease_views=[]
        each_sale_views=[]
        
        
        month=timezone.now() - analytics.last_reset_date
        month=month.days
        
        if month >= 30:
            reset=True
        else:
            reset=False
        
        for prop_id in companies_properties_lease:
            view=property_views_count("Rent", prop_id.pk, reset)
            each_lease_views.append(view)
            
        for prop_id in companies_properties_sale:
            view=property_views_count("Sale", prop_id.pk, reset)
            each_sale_views.append(view)
        
        total_lease_views=sum(each_lease_views)
        total_sale_views=sum(each_sale_views)
        analytics.property_views_l=total_lease_views
        analytics.property_views_s=total_sale_views 
        analytics.save()
        
        total_prop_views = analytics.property_views_l + analytics.property_views_s
        prop_views_on_sale = analytics.property_views_s
        prop_views_on_lease = analytics.property_views_l
        
        lease_views_change=monthly_change(analytics.property_views_l, analytics.last_month_lease_views)
        sale_views_change=monthly_change(analytics.property_views_s, analytics.last_month_sale_views)
        profile_views_change=monthly_change(profile_views, analytics.last_month_profile_views)
        
        total_prop_incr_perc= sale_views_change + lease_views_change/2


        
        '''Competitions'''
        companies= CompanyInformation.objects.all()
        total_companies_eng=[]
        total_company_listings_views= analytics.property_views_s + analytics.property_views_l
        
        
        prop_rent=PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
        prop_sale=PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
        
        
        rent_likes=get_total_likes("Rent", prop_rent)
        sale_likes=get_total_likes("Sale", prop_sale)
        total_liked_prop= rent_likes + sale_likes
        eng_rate=engagement_rate(total_liked_prop,total_company_listings_views, profile_views)
        analytics.competition=eng_rate
        analytics.save()
        
        for comp in companies:
            prop_rent=PropertyManagementRent.objects.filter(company_uuid=comp.unique_company_id)
            prop_sale=PropertyManagementSale.objects.filter(company_uuid=comp.unique_company_id)
            rent_likes=get_total_likes("Rent", prop_rent)
            sale_likes=get_total_likes("Sale", prop_sale)
            total_liked_prop= rent_likes + sale_likes
            
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
        calculated_engagement= total_companies_engagement_calculator(
            total_eng_sum,
            analytics.competition,
            company.unique_company_id,
            total_prop_views
        )
        competition=calculated_engagement[0]
        inq_conv_rate= calculated_engagement[1]
        
        
        '''Most Liked Property'''
        prop_rent = PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
        prop_sale = PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)

        total_property_list = list(prop_rent) + list(prop_sale)

        total_property_list.sort(key=lambda x: x.total_likes, reverse=True)

        total_property_list = total_property_list[:4]
        view_list=[]
        for prop in total_property_list:
            prop_views=PropertyViews.objects.filter(property_type=prop.property_type,property_id=prop.pk).count()
            view_list.append(prop_views)
        likes_views= zip(total_property_list, view_list)
        
        return render(request, 'company/company_analytics.html', {
            'profile_views': profile_views,
            'prop_views': total_prop_views,
            'leased_view': prop_views_on_lease,
            'sale_view': prop_views_on_sale,
            'profile_incr_perc': profile_views_change,
            'lease_incr_perc': lease_views_change,
            'sale_incr_perc': sale_views_change,
            'total_prop_incr_perc': total_prop_incr_perc,
            'engagement_rate': analytics.competition,
            'competition':competition,
            'inq_rate':inq_conv_rate,
            'ranking': likes_views
        })
        
    except CompanyInformation.DoesNotExist:
        messages.error(request, "Company profile not found.")
        return redirect('landing') # Redirect to a safe page if profile is missing
        
    except Exception as e:
        # Catch any unexpected errors (database connection, misconfigured settings, etc.)
        return render(request, 'estate/error_page.html', {'e': str(e)})


def appointment(request):
    if not request.user.is_authenticated:
        messages.info(request, "Login Required")
        return redirect('login')
    if request.user.role != 'company':
        messages.info(request, 'Company account only')
        return redirect('landing')
    try:
        
        '''Client Appointment'''
        #Company in question
        company= CompanyInformation.objects.get(user_id=request.user.id)
        
        total_appointment= Appointments.objects.filter(company_uuid=company.unique_company_id)
        
        
        
        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})
    
    
    
    
    return render(request, 'company/appointment.html', {'appointments': total_appointment})

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
            messages.success(request, "Lead Deleted")
            return redirect('company:lead-management')
        else:
            messages.warning(request, "You aren't authorized to perform that action")
            return redirect('landing')
    except Exception as e:
        return render(request, 'estate/error_page', {e})



@require_POST
def update_lead_status(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'log in to access this page')
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
            messages.error(request, 'Lead Not found')
            return redirect('company:lead-management')
    except Exception as e:
        return render(request, 'estate/error_page.html')



@require_POST
def update_lead_stage(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain access')
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
            messages.error(request, 'Lead Not found')
            return redirect('company:lead-management')
    except Exception as e:
        return render(request, 'estate/error_page.html')



def company_profile(request, company_uuid):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('landing')
    if request.user.role == 'company':
        messages.info(request, 'Access Denied')
        return redirect('landing')
    try:
        company = get_object_or_404(CompanyInformation, unique_company_id=company_uuid)
        
        # Count properties
        total_property_on_lease = PropertyManagementRent.objects.filter(company_uuid=company_uuid).count()
        total_property_on_sale = PropertyManagementSale.objects.filter(company_uuid=company_uuid).count()
        total_properties = total_property_on_lease + total_property_on_sale
        
        # Get social links
        social_links = company.social.all()
        
        # Property querysets
        on_sale_qs = PropertyManagementSale.objects.filter(company_uuid=company_uuid)
        on_lease_qs = PropertyManagementRent.objects.filter(company_uuid=company_uuid)
        
        # Pagination (2 items per page)
        p_sale = Paginator(on_sale_qs, 2)
        p_lease = Paginator(on_lease_qs, 2)
        
        page_sale = request.GET.get('page_sale', 1)
        page_rent = request.GET.get('page_rent', 1)
        
        properties_on_sale = p_sale.get_page(page_sale)
        properties_on_lease = p_lease.get_page(page_rent)
        
        # Get reviews and calculate average rating
        reviews = CompanyRating.objects.filter(company_uuid=company_uuid).select_related('user')
        rating_data = reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        average_rating = rating_data['avg_rating'] or 0.0
        total_reviews = rating_data['total_reviews']
        
        # Check if user has already reviewed (if authenticated)
        user_has_reviewed = False
        if request.user.is_authenticated:
            user_has_reviewed = reviews.filter(user=request.user).exists()
            
            # Track profile view
            try:
                prop_analytics = company.session_id.get(session_id=request.user.id)
            except ObjectDoesNotExist:
                prop_analytics = SessionId.objects.create(
                    company=company,
                    session_id=request.user.id,
                    inquires_check=0
                )
                profile = company.analytics.get()
                profile.profile_views += 1
                profile.save()
        
        # Generate page numbers for pagination
        nums_sale = "x" * properties_on_sale.paginator.num_pages
        nums_rent = "x" * properties_on_lease.paginator.num_pages
        
        context = {
            'company': company,
            'total_properties': total_properties,
            'properties_for_sale': total_property_on_sale,
            'properties_for_rent': total_property_on_lease,
            'social_links': social_links,
            'on_lease': properties_on_lease,
            'on_sale': properties_on_sale,
            'nums_s': nums_sale,
            'nums_r': nums_rent,
            'reviews': reviews[:5],  # Show only 5 most recent
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'user_has_reviewed': user_has_reviewed,
        }
        
        return render(request, 'company/company_profile.html', context)
        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})


def properties_by_company(request, company_uuid):
    if request.user.is_authenticated:
        if request.user.role == 'company':
            messages.info(request, 'Customer\'s only')
            return redirect('company:dashboard')
        company=CompanyInformation.objects.get(unique_company_id=company_uuid)
        on_lease=PropertyManagementRent.objects.filter(company_uuid=company_uuid)
        on_sale=PropertyManagementSale.objects.filter(company_uuid=company_uuid)
        return render(request, 'company/company_properties.html', {
            'on_lease': on_lease,
            'on_sale': on_sale,
            'company':company
        })
        



