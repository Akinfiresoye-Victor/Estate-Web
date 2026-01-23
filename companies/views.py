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




def monthly_change(present_data, last_month_data):
    if last_month_data == 0:
        return 100 if present_data > 0 else 0
    return ((present_data - last_month_data) / last_month_data) * 100


def engagement_rate(total_liked_prop, total_company_listings_views, profile_views, ratings):
    total_engagements = total_liked_prop + total_company_listings_views + profile_views + ratings
    user_count = User.objects.count()
    return (total_engagements / user_count) * 100 if user_count > 0 else 0


def get_total_likes(property_type, properties):
    return properties.aggregate(total=Sum('total_likes'))['total'] or 0


def total_companies_engagement_calculator(total_rate, personal_rate, personal_uuid, property_views):
    total_company_competition = (personal_rate / total_rate) * 100 if total_rate > 0 else 0
    
    total_impression = LeadInfo.objects.filter(company_uuid=personal_uuid).count()
    expression_rate = (total_impression / property_views) * 100 if property_views > 0 else 0
    
    return [total_company_competition, expression_rate]


def reset_button(general_data, company_uuid, lease_views, sale_views):
    days_since_reset = (timezone.now() - general_data.last_reset_date).days
    
    if days_since_reset >= 30:
        general_data.average_profile_views = (general_data.profile_views + general_data.average_profile_views) / 2
        general_data.average_lease_views = (lease_views + general_data.average_lease_views) / 2
        general_data.average_sale_views = (sale_views + general_data.average_sale_views) / 2
        general_data.profile_views = 0
        general_data.property_views_l = 0
        general_data.property_views_s = 0
        general_data.last_reset_date = timezone.now()
        general_data.save()
        
        PropertyViews.objects.filter(uuid=company_uuid).delete()
        SessionId.objects.all().delete()


def property_views_count(property_type, property_id):
    return PropertyViews.objects.filter(
        property_type=property_type,
        property_id=property_id
    ).count()





#Companies dashboard
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
        
        # Get or create analytics
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
        
        # Calculate property views in bulk
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
        
        # Update analytics
        analytics.property_views_l = lease_views
        analytics.property_views_s = sale_views
        analytics.save()
        
        reset_button(analytics, company.unique_company_id, lease_views, sale_views)
        
        # Get counts efficiently
        total_prop = (
            PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id).count() +
            PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id).count()
        )
        total_inq = LeadInfo.objects.filter(company_uuid=company.unique_company_id).count()
        
        # Get rating data
        rating_data = CompanyRating.objects.filter(
            company_uuid=company.unique_company_id
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        average_rating = rating_data['avg_rating'] or 0.0
        total_reviews = rating_data['total_reviews']
        
        # Calculate engagement for current company
        prop_rent = PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
        prop_sale = PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
        
        rent_likes = prop_rent.aggregate(total=Sum('total_likes'))['total'] or 0
        sale_likes = prop_sale.aggregate(total=Sum('total_likes'))['total'] or 0
        total_liked_prop = rent_likes + sale_likes
        
        averg_rating = average_rating * total_reviews
        avg_property_view = analytics.average_lease_views + analytics.average_sale_views
        
        eng_rate = engagement_rate(
            total_liked_prop,
            avg_property_view,
            analytics.average_profile_views,
            averg_rating
        )
        analytics.competition = eng_rate
        analytics.save()
        
        # Calculate competition scores for all companies
        total_eng = []
        companies = CompanyInformation.objects.prefetch_related('analytics').all()
        
        for comp in companies:
            comp_analytics, _ = CompanyAnalytics.objects.get_or_create(
                company=comp,
                defaults={
                    'profile_views': 0,
                    'property_views_l': 0,
                    'property_views_s': 0,
                    'average_profile_views': 0,
                    'average_lease_views': 0,
                    'average_sale_views': 0,
                }
            )
            
            # Get likes in bulk
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
            avg_rating = comp_avg_rating * comp_total_reviews
            
            avg_prop_views = comp_analytics.average_sale_views + comp_analytics.average_lease_views
            
            comp_eng_rate = engagement_rate(
                comp_total_likes,
                avg_prop_views,
                comp_analytics.average_profile_views,
                avg_rating
            )
            
            total_eng.append(comp_eng_rate)
        
        # Calculate competition
        total_eng_sum = sum(total_eng)
        calculated_engagement = total_companies_engagement_calculator(
            total_eng_sum,
            analytics.competition,
            company.unique_company_id,
            avg_property_view
        )
        
        # Calculate market position (Top X%)
        if total_eng and len(total_eng) > 1:
            # Sort companies by engagement (descending)
            sorted_eng = sorted(total_eng, reverse=True)
            # Count how many companies have higher engagement
            companies_above = sum(1 for eng in sorted_eng if eng > analytics.competition)
            # Calculate percentile (what % of companies you're better than)
            market_position = ((companies_above) / len(sorted_eng)) * 100
            
            # Determine if top 1%, 5%, 10%, etc.
            if market_position < 1:
                top_performer = "Top 1%"
            elif market_position < 5:
                top_performer = "Top 5%"
            elif market_position < 10:
                top_performer = "Top 10%"
            elif market_position < 25:
                top_performer = "Top 25%"
            elif market_position < 50:
                top_performer = "Top 50%"
            else:
                top_performer = f"Top {int(market_position + 1)}%"
        else:
            top_performer = "New Listing"
            market_position = 0
        
        competition = calculated_engagement[0]
        
        context = {
            'company': company,
            'social_links': social_links,
            'total_properties': total_prop,
            'total_views': profile_views,
            'total_inquiries': total_inq,
            'average_rating': average_rating,
            'competition': top_performer,
            'market_position': round(market_position, 1)
        }
        
        return render(request, 'company/dashboard.html', context)
        
    except CompanyInformation.DoesNotExist:
        messages.warning(request, 'Set company profile')
        return redirect('company:company_form')
        
    except Exception as e:
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
        
        # Get or create analytics
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
        
        # Get rating data efficiently
        rating_data = CompanyRating.objects.filter(
            company_uuid=company.unique_company_id
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        average_rating = rating_data['avg_rating'] or 0.0
        total_reviews = rating_data['total_reviews']
        
        # Calculate property views in bulk
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
        
        # Update analytics
        analytics.property_views_l = lease_views
        analytics.property_views_s = sale_views
        analytics.save()
        
        reset_button(analytics, company.unique_company_id, lease_views, sale_views)
        
        # Calculate changes
        lease_views_change = monthly_change(analytics.property_views_l, analytics.average_lease_views)
        sale_views_change = monthly_change(analytics.property_views_s, analytics.average_sale_views)
        profile_views_change = monthly_change(analytics.profile_views, analytics.average_profile_views)
        total_prop_incr_perc = (sale_views_change + lease_views_change) / 2
        
        # Calculate engagement for current company
        prop_rent = PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id)
        prop_sale = PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id)
        
        rent_likes = prop_rent.aggregate(total=Sum('total_likes'))['total'] or 0
        sale_likes = prop_sale.aggregate(total=Sum('total_likes'))['total'] or 0
        total_liked_prop = rent_likes + sale_likes
        
        avg_prop_views = analytics.average_lease_views + analytics.average_sale_views
        averg_rating = average_rating * total_reviews
        
        eng_rate = engagement_rate(
            total_liked_prop,
            avg_prop_views,
            analytics.average_profile_views,
            averg_rating
        )
        analytics.competition = eng_rate
        analytics.save()
        
        # Calculate competition scores for all companies
        total_companies_eng = []
        companies = CompanyInformation.objects.prefetch_related('analytics').all()
        
        for comp in companies:
            comp_analytics, _ = CompanyAnalytics.objects.get_or_create(
                company=comp,
                defaults={
                    'profile_views': 0,
                    'property_views_l': 0,
                    'property_views_s': 0,
                    'average_profile_views': 0,
                    'average_lease_views': 0,
                    'average_sale_views': 0,
                }
            )
            
            # Get likes in bulk
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
            comp_averg_rating = comp_avg_rating * comp_total_reviews
            
            comp_avg_prop_views = comp_analytics.average_sale_views + comp_analytics.average_lease_views
            
            comp_eng_rate = engagement_rate(
                comp_total_likes,
                comp_avg_prop_views,
                comp_analytics.average_profile_views,
                comp_averg_rating
            )
            
            total_companies_eng.append(comp_eng_rate)
        
        # Calculate competition
        total_eng_sum = sum(total_companies_eng)
        calculated_engagement = total_companies_engagement_calculator(
            total_eng_sum,
            analytics.competition,
            company.unique_company_id,
            avg_prop_views
        )
        
        # Calculate market position (Top X%)
        if total_companies_eng and len(total_companies_eng) > 1:
            # Sort companies by engagement (descending)
            sorted_eng = sorted(total_companies_eng, reverse=True)
            # Find current company's rank
            companies_above= sum(1 for eng in sorted_eng if eng > analytics.competition)
            # Calculate percentile
            market_position = (companies_above / len(sorted_eng)) * 100
            # Determine if top 1%, 5%, 10%, etc.
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
        
        competition = calculated_engagement[0]
        inq_conv_rate = calculated_engagement[1]
        
        # Get most liked properties with views
        all_properties = list(prop_rent) + list(prop_sale)
        all_properties.sort(key=lambda x: x.total_likes, reverse=True)
        top_properties = all_properties[:4]
        
        # Get views for top properties in bulk
        rent_ids = [p.pk for p in top_properties if p.property_type == 'Rent']
        sale_ids = [p.pk for p in top_properties if p.property_type == 'Sale']
        
        rent_view_counts = PropertyViews.objects.filter(
            property_type='Rent',
            property_id__in=rent_ids
        ).values('property_id').annotate(count=Count('id'))
        
        sale_view_counts = PropertyViews.objects.filter(
            property_type='Sale',
            property_id__in=sale_ids
        ).values('property_id').annotate(count=Count('id'))
        
        # Create lookup dictionaries
        rent_views_dict = {v['property_id']: v['count'] for v in rent_view_counts}
        sale_views_dict = {v['property_id']: v['count'] for v in sale_view_counts}
        
        view_list = []
        for prop in top_properties:
            if prop.property_type == 'Rent':
                view_list.append(rent_views_dict.get(prop.pk, 0))
            else:
                view_list.append(sale_views_dict.get(prop.pk, 0))
        
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
        return render(request, 'estate/error_page.html', {'e': str(e)})


def documents(request):
    return render(request, 'company/documents.html', {})

def reports(request):
    pass

def company_settings(request):
    return render(request, 'company/company_settings.html')


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