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
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Sum
from core.utils import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm








def dashboard(request):
    if not request.user.is_authenticated:
        messages.info(request, 'log in to access page')
        return redirect('landing')
        
    if request.user.role != 'company':
        messages.error(request, 'Company account only')
        return redirect('landing')

    try:
        company = CompanyInformation.objects.get(user_id=request.user.id)
        social_links = company.social.all()
        
        # Get or create analytics for CURRENT company
        analytics, _ = CompanyAnalytics.objects.get_or_create(
            company=company,
            defaults={
                'profile_views': 0,
                'property_views_l': 0,
                'property_views_s': 0,
                'average_profile_views': 0,
                'average_lease_views': 0,
                'average_sale_views': 0,
            }
        )
        
        profile_views = analytics.profile_views
        
        # Calculate property views for CURRENT company
        lease_views = PropertyViews.objects.filter(
            property_type='Rent',
            property_id__in=PropertyManagementRent.objects.filter(
                company_uuid=company.unique_company_id
            ).values_list('pk', flat=True)
        ).count()
        
        sale_views = PropertyViews.objects.filter(
            property_type='Sale',
            property_id__in=PropertyManagementSale.objects.filter(
                company_uuid=company.unique_company_id
            ).values_list('pk', flat=True)
        ).count()
        
        # Update analytics for CURRENT company
        analytics.property_views_l = lease_views
        analytics.property_views_s = sale_views
        analytics.save()
        
        # Reset monthly tracking if needed
        reset_button(analytics, company.unique_company_id, lease_views, sale_views)
        
        # Get counts efficiently for CURRENT company
        total_prop = (
            PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id).count() +
            PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id).count()
        )
        total_inq = LeadInfo.objects.filter(company_uuid=company.unique_company_id).count()
        
        # Get rating data for CURRENT company
        rating_data = CompanyRating.objects.filter(
            company_uuid=company.unique_company_id
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        average_rating = rating_data['avg_rating'] or 0.0
        total_reviews = rating_data['total_reviews']
        
        # Calculate engagement for CURRENT company
        prop_rent = PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
        prop_sale = PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
        
        rent_likes = prop_rent.aggregate(total=Sum('total_likes'))['total'] or 0
        sale_likes = prop_sale.aggregate(total=Sum('total_likes'))['total'] or 0
        total_liked_prop = rent_likes + sale_likes
        
        rating_score = average_rating * total_reviews
        avg_property_view = analytics.average_lease_views + analytics.average_sale_views
        
        eng_rate = engagement_rate(
            total_liked_prop,
            avg_property_view,
            analytics.average_profile_views,
            rating_score
        )
        
        # Save engagement score for CURRENT company
        analytics.competition = eng_rate
        analytics.save()
        
        # Get ALL companies' analytics in one query (READ ONLY - don't modify!)
        all_analytics = CompanyAnalytics.objects.select_related('company').all()
        
        total_eng = []
        
        for comp_analytics in all_analytics:
            comp = comp_analytics.company
            
            # Calculate engagement using EXISTING data (don't modify!)
            comp_rent_likes = PropertyManagementRent.objects.filter(
                company_uuid=comp.unique_company_id
            ).aggregate(total=Sum('total_likes'))['total'] or 0
            
            comp_sale_likes = PropertyManagementSale.objects.filter(
                company_uuid=comp.unique_company_id
            ).aggregate(total=Sum('total_likes'))['total'] or 0
            
            comp_total_likes = comp_rent_likes + comp_sale_likes
            
            # Get rating data
            comp_rating_data = CompanyRating.objects.filter(
                company_uuid=comp.unique_company_id
            ).aggregate(
                avg_rating=Avg('rating'),
                total_reviews=Count('id')
            )
            comp_avg_rating = comp_rating_data['avg_rating'] or 0.0
            comp_total_reviews = comp_rating_data['total_reviews']
            comp_rating_score = comp_avg_rating * comp_total_reviews
            
            comp_avg_prop_views = comp_analytics.average_sale_views + comp_analytics.average_lease_views
            
            # Calculate engagement score
            comp_eng_rate = engagement_rate(
                comp_total_likes,
                comp_avg_prop_views,
                comp_analytics.average_profile_views,
                comp_rating_score
            )
            
            total_eng.append(comp_eng_rate)
            
            # If this is the current company, we already saved their score above
        
        total_eng_sum = sum(total_eng)
        calculated_engagement = total_companies_engagement_calculator(
            total_eng_sum,
            analytics.competition,
            company.unique_company_id,
            avg_property_view
        )
        
        # Calculate market position (Top X%)
        if total_eng and len(total_eng) > 1:
            sorted_eng = sorted(total_eng, reverse=True)
            companies_above = sum(1 for eng in sorted_eng if eng > analytics.competition)
            market_position = (companies_above / len(sorted_eng)) * 100
            
            if market_position <= 1:
                top_performer = "Top 1%"
            elif market_position <= 5:
                top_performer = "Top 5%"
            elif market_position <= 10:
                top_performer = "Top 10%"
            elif market_position <= 25:
                top_performer = "Top 25%"
            elif market_position <= 50:
                top_performer = "Top 50%"
            else:
                top_performer = f"Top {int(market_position)}%"
        else:
            top_performer = "New Listing"
            market_position = 100
        
        competition_pct = calculated_engagement[0]
        
        
        context = {
            'company': company,
            'social_links': social_links,
            'total_properties': total_prop,
            'total_views': profile_views,
            'total_inquiries': total_inq,
            'average_rating': average_rating,
            'total_reviews': total_reviews,
            'competition': top_performer,
            'market_position': round(market_position, 1),
            'engagement_rate': analytics.competition
        }
        
        return render(request, 'company/dashboard.html', context)
        
    except CompanyInformation.DoesNotExist:
        messages.warning(request, 'Set company profile')
        return redirect('company:company_form')
        
    except Exception as e:
        print(f"Error in company dashboard: {e}")  # Debug logging
        return render(request, 'estate/error_page.html', {'e': e})


#form all companies must fill before they access the dashboard
def company_form(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'company':
        messages.error(request, 'Company account only')
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
        return render(request, 'estate/error_page.html', {'e': e})


def update_company_profile(request, company_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'company':
        messages.info(request, 'Company account only')
        return redirect('landing')
    try:
        company_information=CompanyInformation.objects.get(unique_company_id=company_id)
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
                        return redirect('company:company-settings')
            else:
                comp_form = CompanyForm(instance=company_information)
                link_form = SocialLinksFormset(instance=company_information)
            return render(request, 'company/update_company_profile.html', {
                'form':comp_form,
                'social': link_form
            })
        else:
            messages.warning(request, 'Access Denied')
            return redirect('landing')
    except ObjectDoesNotExist:
        messages.info(request, 'Company data missing')
        return redirect('landing')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})


def company_analytics(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'login Required')
        return redirect('login')
        
    if request.user.role != 'company':
        messages.error(request, 'Company account only')
        return redirect('landing')

    try:
        messages.info(request, 'Numbers might seem low since we just launched')
        company = CompanyInformation.objects.get(user_id=request.user.id)
        analytics, _ = CompanyAnalytics.objects.get_or_create(
            company=company,
            defaults={
                'profile_views': 0,
                'property_views_l': 0,
                'property_views_s': 0,
                'average_profile_views': 0,
                'average_lease_views': 0,
                'average_sale_views': 0,
            }
        )
        
        # Get rating data for CURRENT company
        rating_data = CompanyRating.objects.filter(
            company_uuid=company.unique_company_id
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        average_rating = rating_data['avg_rating'] or 0.0
        total_reviews = rating_data['total_reviews']
        
        # Calculate property views for CURRENT company
        lease_views = PropertyViews.objects.filter(
            property_type='Rent',
            property_id__in=PropertyManagementRent.objects.filter(
                company_uuid=company.unique_company_id
            ).values_list('pk', flat=True)
        ).count()
        
        sale_views = PropertyViews.objects.filter(
            property_type='Sale',
            property_id__in=PropertyManagementSale.objects.filter(
                company_uuid=company.unique_company_id
            ).values_list('pk', flat=True)
        ).count()
        
        # Update analytics for CURRENT company
        analytics.property_views_l = lease_views
        analytics.property_views_s = sale_views
        analytics.save()
        
        # Reset monthly tracking if needed
        reset_button(analytics, company.unique_company_id, lease_views, sale_views)
        
        # Calculate percentage changes
        lease_views_change = monthly_change(analytics.property_views_l, analytics.average_lease_views)
        sale_views_change = monthly_change(analytics.property_views_s, analytics.average_sale_views)
        profile_views_change = monthly_change(analytics.profile_views, analytics.average_profile_views)
        total_prop_incr_perc = (sale_views_change + lease_views_change) / 2
        
        # Calculate engagement for CURRENT company
        prop_rent = PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
        prop_sale = PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
        
        rent_likes = prop_rent.aggregate(total=Sum('total_likes'))['total'] or 0
        sale_likes = prop_sale.aggregate(total=Sum('total_likes'))['total'] or 0
        total_liked_prop = rent_likes + sale_likes
        
        avg_prop_views = analytics.average_lease_views + analytics.average_sale_views
        rating_score = average_rating * total_reviews
        
        eng_rate = engagement_rate(
            total_liked_prop,
            avg_prop_views,
            analytics.average_profile_views,
            rating_score
        )
        analytics.competition = eng_rate
        analytics.save()
        
        
        # Get ALL companies' analytics in one query (READ ONLY)
        all_analytics = CompanyAnalytics.objects.select_related('company').all()
        
        total_companies_eng = []
        
        for comp_analytics in all_analytics:
            comp = comp_analytics.company
            
            # Calculate engagement using EXISTING data (don't modify!)
            comp_rent_likes = PropertyManagementRent.objects.filter(
                company_uuid=comp.unique_company_id
            ).aggregate(total=Sum('total_likes'))['total'] or 0
            
            comp_sale_likes = PropertyManagementSale.objects.filter(
                company_uuid=comp.unique_company_id
            ).aggregate(total=Sum('total_likes'))['total'] or 0
            
            comp_total_likes = comp_rent_likes + comp_sale_likes
            
            # Get rating data
            comp_rating_data = CompanyRating.objects.filter(
                company_uuid=comp.unique_company_id
            ).aggregate(
                avg_rating=Avg('rating'),
                total_reviews=Count('id')
            )
            comp_avg_rating = comp_rating_data['avg_rating'] or 0.0
            comp_total_reviews = comp_rating_data['total_reviews']
            comp_rating_score = comp_avg_rating * comp_total_reviews
            
            comp_avg_prop_views = comp_analytics.average_sale_views + comp_analytics.average_lease_views
            
            comp_eng_rate = engagement_rate(
                comp_total_likes,
                comp_avg_prop_views,
                comp_analytics.average_profile_views,
                comp_rating_score
            )
            
            total_companies_eng.append(comp_eng_rate)
            
            # If this is the current company, we already saved their score above
        
        
        total_eng_sum = sum(total_companies_eng)
        calculated_engagement = total_companies_engagement_calculator(
            total_eng_sum,
            analytics.competition,
            company.unique_company_id,
            avg_prop_views
        )
        
        # Calculate market position (Top X%)
        if total_companies_eng and len(total_companies_eng) > 1:
            sorted_eng = sorted(total_companies_eng, reverse=True)
            companies_above = sum(1 for eng in sorted_eng if eng > analytics.competition)
            market_position = (companies_above / len(sorted_eng)) * 100
            
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
            top_performer = "New Listing"
            market_position = 100
        
        competition_pct = calculated_engagement[0]
        inq_conv_rate = calculated_engagement[1]
        
        
        all_properties = list(prop_rent) + list(prop_sale)
        all_properties.sort(key=lambda x: x.total_likes, reverse=True)
        top_properties = all_properties[:4]
        
        # Get views for top 4 properties efficiently
        view_list = []
        for prop in top_properties:
            cnt = PropertyViews.objects.filter(
                property_id=prop.pk,
                property_type=prop.property_type
            ).count()
            view_list.append(cnt)
        
        likes_views = zip(top_properties, view_list)
        
        return render(request, 'company/company_analytics.html', {
            'profile_views': analytics.profile_views,
            'prop_views': analytics.property_views_l + analytics.property_views_s,
            'leased_view': analytics.property_views_l,
            'sale_view': analytics.property_views_s,
            'profile_incr_perc': profile_views_change,
            'lease_incr_perc': lease_views_change,
            'sale_incr_perc': sale_views_change,
            'total_prop_incr_perc': total_prop_incr_perc,
            'engagement_rate': analytics.competition,
            'competition': top_performer,
            'market_position': round(market_position, 1),
            'inq_rate': inq_conv_rate,
            'ranking': likes_views
        })
        
    except CompanyInformation.DoesNotExist:
        messages.error(request, "Company profile not found.")
        return redirect('landing')
        
    except Exception as e:
        print(f"Error in company_analytics: {e}")  # Debug logging
        return render(request, 'estate/error_page.html', {'e': str(e)})



def documents(request):
    return render(request, 'company/documents.html', {})

def reports(request):
    pass

def company_settings(request):
    
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'company':
        messages.error(request, 'Companies Only')
        return redirect('landing')
    
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)
        context={
            'company':company,
        }
        return render(request, 'company/company_settings.html', context)
    except ObjectDoesNotExist:
        messages.error(request, 'Error Company Info Missing')
        return redirect('landing')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})


def lead_management(request):
    try:
        if not request.user.is_authenticated:
            messages.info(request, 'Login required')
            return redirect('login')
        if request.user.role != 'company':
            messages.error(request, 'Company account only')
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
    if not request.user.is_authenticated:
        messages.info(request, 'Login required')
        return redirect('login')
    if request.user.role != 'company':
        messages.info(request, 'Company account only')
        return redirect('landing')
    try:
        company=CompanyInformation.objects.get(user_id=request.user.id)
        data=LeadInfo.objects.get(lead_id=lead_id)
        if data.company_uuid == company.unique_company_id:
            client=data
        else:
            messages.warning(request, 'Access Denied')
            return redirect('landing')
        if client.property_type =='Sale' :
            property=PropertyManagementSale.objects.get(pk=client.property_intrested)
        elif client.property_type == 'Rent':
            property=PropertyManagementRent.objects.get(pk=client.property_intrested)
        else:
            property=None
        return render(request, 'company/lead_detail_page.html', {'lead':client, 'property':property})
    except Exception as e:
        return render(request, 'estate/error_page', {'e': e})

#FIXME if a property is deleted all models pointing to that property must be deleted also


def delete_lead(request, lead_id):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role != 'company':
        messages.error(request, 'Access denied')
        return redirect('landing')
    try:
        company= CompanyInformation.objects.get(user_id=request.user.id)
        lead_to_delete=LeadInfo.objects.get(lead_id=lead_id)
        if company.unique_company_id == lead_to_delete.company_uuid:
            lead_to_delete.delete()
            messages.success(request, "Lead Deleted")
            return redirect('company:lead-management')
        else:
            messages.error(request, "Access Denied")
            return redirect('landing')
    except Exception as e:
        return render(request, 'estate/error_page', {'e': e})



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
            company= CompanyInformation.objects.get(user_id= request.user.id)
            lead_data=LeadInfo.objects.get(pk=lead_id)
            if lead_data.company_uuid == company.unique_company_id:
                lead=lead_data
            else:
                messages.error(request, 'Access Denied')
                return redirect('landing')
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
        return render(request, 'estate/error_page.html', {'e':e})



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
            company= CompanyInformation.objects.get(user_id= request.user.id)
            lead_data=LeadInfo.objects.get(pk=lead_id)
            if lead_data.company_uuid == company.unique_company_id:
                lead=lead_data
            else:
                messages.error(request, 'Access Denied')
                return redirect('landing')
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
        return render(request, 'estate/error_page.html', {'e':e})



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
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('login')
    if request.user.role !='customer':
        messages.info(request, 'Customers Only')
        return redirect('landing')
    try:
        company=CompanyInformation.objects.get(unique_company_id=company_uuid)
        on_lease=PropertyManagementRent.objects.filter(company_uuid=company_uuid)
        on_sale=PropertyManagementSale.objects.filter(company_uuid=company_uuid)
        return render(request, 'company/company_properties.html', {
            'on_lease': on_lease,
            'on_sale': on_sale,
            'company':company
        })
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})



def find_talents(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('landing')
    if request.user.role !='company':
        messages.info(request, 'Company Account Only')
        return redirect('landing')
    
    try:
        return render(request, 'company/find_talents.html')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})


def manage_applications(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('landing')
    if request.user.role !='company':
        messages.info(request, 'Company Account Only')
        return redirect('landing')
    
    try:
        return render(request, 'company/manage_applications.html')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})


def manage_company(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('landing')
    if request.user.role !='company':
        messages.info(request, 'Company Account Only')
        return redirect('landing')
    
    try:
        return render(request, 'company/manage_company.html')
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e':e})




def delete_company():
    pass

def change_password(request):
    """
    Change User Passwords with precise lines of code
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain acess')
        return redirect('login')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        if request.method == 'POST':
            form= PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                new_pass=form.save() 
                update_session_auth_hash(request, new_pass)
                messages.success(request, 'Password Changed successfully')
                return redirect('customer:password-success')
            
            else:
                messages.error(request, 'Error Changing password...')
                return redirect('customer:change-password')
            
        else:
            form= PasswordChangeForm(request.user)
            return render(request, 'estate/change_passw.html', {'form': form, 'base_template':base_template})
        
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})



def change_password_success(request):
    """
    Success Page after chaging password
    """
    if not request.user.is_authenticated:
        messages.info(request, 'Log in to gain access')
        return redirect('login')
    if not request.user.role == 'customer':
        messages.info(request, 'Congrats after messing around youve seen the green button')
    try:
        user_role=request.user.role
        if user_role == 'company':
            base_template = 'company/base.html'
        elif user_role == 'agent':
            base_template = 'agent/base.html'
        else:
            base_template='estate/base.html'
        return render(request, 'estate/succ_pass.html', {'base_template', base_template})
    
    except Exception as e:
        return render(request, 'estate/error_page.html', {'e': e})
