from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.template import TemplateDoesNotExist
from agents.models import AgentInformation
from companies.models import CompanyInformation, SessionId
from core.models import PropertyManagementRent, PropertyManagementSale, PropertyViews, WishlistStorageUnit, ErrorLog
from estate.models import LeadInfo
import traceback

def agent_reset_button(analytics, agent_uuid, lease_views, sale_views):
    """Reset monthly tracking if 30 days have passed"""
    
    current_time = timezone.now()
    time_difference = current_time - analytics.last_reset_date
    
    if time_difference >= timedelta(days=30):
        # Calculate new averages
        total_profile = analytics.profile_views + analytics.average_profile_views
        total_lease = lease_views + analytics.average_lease_views
        total_sale = sale_views + analytics.average_sale_views
        
        # Update averages
        analytics.average_profile_views = total_profile // 2
        analytics.average_lease_views = total_lease // 2
        analytics.average_sale_views = total_sale // 2
        
        # Reset current counters
        analytics.profile_views = 0
        analytics.property_views_l = 0
        analytics.property_views_s = 0
        analytics.last_reset_date = current_time
        
        analytics.save()


def total_agents_engagement_calculator(total_eng_sum, current_engagement, agent_uuid, avg_prop_views):
    """
    Calculate market position and inquiry conversion rate
    Returns: [competition_percentage, inquiry_rate]
    """
    from estate.models import LeadInfo
    
    if total_eng_sum == 0:
        competition = 0
    else:
        competition = (current_engagement / total_eng_sum) * 100
    
    # Calculate inquiry conversion rate
    leads = LeadInfo.objects.filter(agent_id=agent_uuid).count()
    
    if avg_prop_views == 0:
        inq_rate = 0
    else:
        inq_rate = (leads / max(avg_prop_views, 1)) * 100
        inq_rate = min(inq_rate, 100)  # Cap at 100%
    
    return [round(competition, 2), round(inq_rate, 2)]






def monthly_change(current_value, average_value):
    """
    Calculate percentage change from average
    
    Plain English:
    - If you had 100 views last month and 150 this month = +50%
    - If you had 200 views last month and 150 this month = -25%
    """
    if average_value == 0:
        return 0 if current_value == 0 else 100
    change = ((current_value - average_value) / average_value) * 100
    return round(change, 2)


def engagement_rate(total_likes, avg_property_views, avg_profile_views, rating_score):
    """
    Calculate engagement score (0-100) based on weighted factors
    
    Plain English:
    - 40% weight: How many people wishlisted your properties (shows serious interest)
    - 30% weight: How many property views you get (shows people are looking)
    - 20% weight: How many profile views you get (shows brand awareness)
    - 10% weight: Your ratings (stars × reviews = quality confirmation)
    
    Example:
    - 100 total likes → 40 points
    - 500 property views → 30 points  
    - 50 profile views → 20 points
    - 4.5 stars × 20 reviews = 90 → 10 points
    Total = 100 points (perfect engagement)
    """
    if avg_property_views == 0 and avg_profile_views == 0:
        return 0.0
    
    # Weighted engagement calculation
    like_weight = 0.4      # 40% - Most important (wishlist = intent)
    view_weight = 0.3      # 30% - Important (views = interest)
    profile_weight = 0.2   # 20% - Moderate (brand awareness)
    rating_weight = 0.1    # 10% - Confirmation (quality proof)
    
    # Normalize values to 0-100 scale
    like_score = min(total_likes / max(1, avg_property_views / 10), 100) * like_weight
    view_score = min(avg_property_views / 10, 100) * view_weight
    profile_score = min(avg_profile_views / 5, 100) * profile_weight
    rating_score_normalized = min(rating_score * 2, 100) * rating_weight
    
    total_engagement = like_score + view_score + profile_score + rating_score_normalized
    
    return round(total_engagement, 2)


def total_companies_engagement_calculator(total_eng_sum, current_engagement, company_uuid, avg_prop_views):
    """
    Calculate market share and inquiry conversion rate
    
    Plain English - Competition:
    - If all companies have 1000 engagement points total
    - And you have 150 engagement points
    - You own 15% of the market
    
    Plain English - Inquiry Rate:
    - If your properties get 500 views per month
    - And you receive 50 inquiries
    - Conversion rate = 10% (50 ÷ 500 × 100)
    - Meaning: 1 out of every 10 viewers contacts you
    """
    # Competition percentage (your share of total market engagement)
    if total_eng_sum == 0:
        competition = 0
    else:
        competition = (current_engagement / total_eng_sum) * 100
    
    # Inquiry conversion rate (how many viewers become leads)
    total_inquiries = LeadInfo.objects.filter(company_uuid=company_uuid).count()
    
    if avg_prop_views == 0:
        inquiry_rate = 0
    else:
        inquiry_rate = (total_inquiries / max(avg_prop_views, 1)) * 100
        inquiry_rate = min(inquiry_rate, 100)  # Cap at 100%
    
    return [round(competition, 2), round(inquiry_rate, 2)]

def reset_button(analytics, company_uuid, lease_views, sale_views, current_inquiries, current_ratings):
    """
    Soft reset every 30 days.
    
    - Calculates rolling averages for views, inquiries, ratings
    - Stores last month's values so percentage change can be calculated
    - Resets view counters to 0
    - Does NOT delete any records — queries use date filters instead
    - Updates period_start so the 30-day window restarts cleanly
    """
    current_time = timezone.now()
    time_difference = current_time - analytics.last_reset_date

    if time_difference >= timedelta(days=30):

        # ── Rolling averages (views) ────────────────────────────────────────
        analytics.average_profile_views = (
            analytics.profile_views + analytics.average_profile_views
        ) // 2
        analytics.average_lease_views = (
            lease_views + analytics.average_lease_views
        ) // 2
        analytics.average_sale_views = (
            sale_views + analytics.average_sale_views
        ) // 2

        # ── Rolling averages (inquiries + ratings) ──────────────────────────
        analytics.average_inquiries = (
            current_inquiries + analytics.average_inquiries
        ) // 2
        analytics.average_ratings = (
            current_ratings + analytics.average_ratings
        ) // 2

        # ── Store last month's values for percentage change display ─────────
        analytics.last_month_inquiries = current_inquiries
        analytics.last_month_ratings   = current_ratings

        # ── Reset view counters — inquiries/ratings don't need resetting ────
        # because they are always calculated with a date filter, not stored counts
        analytics.profile_views    = 0
        analytics.property_views_l = 0
        analytics.property_views_s = 0

        # ── Move the 30-day window forward ──────────────────────────────────
        analytics.last_reset_date = current_time
        analytics.period_start    = current_time

        analytics.save()

        # ── Clean up view tracking (these are the only hard deletes) ────────
        # PropertyViews are deleted because they are already aggregated
        # into the rolling averages above — keeping them would double-count
        PropertyViews.objects.filter(uuid=company_uuid).delete()
        SessionId.objects.filter(company_uuid=company_uuid).delete()

def property_views_count(property_type, property_id):
    """
    Count how many times a specific property was viewed
    
    Plain English:
    - Looks in the PropertyViews table
    - Finds all records matching this property
    - Counts them up
    """
    from core.models import PropertyViews
    return PropertyViews.objects.filter(
        property_type=property_type,
        property_id=property_id
    ).count()
    
    







# ── helpers ───────────────────────────────────────────────────────────────────

def _get_description(property_obj, property_type):
    """Both models store the description under different field names."""
    if property_type == 'Rent':
        return getattr(property_obj, 'description', '') or ''
    return getattr(property_obj, 'property_description', '') or ''


def _is_verified_lister(property_obj):
    """
    Returns True if the lister (agent, company, landlord) is verified.
    Imported inside the function to avoid circular imports.
    """
    try:


        if property_obj.agent_uuid and property_obj.agent_uuid != 'None':
            agent = AgentInformation.objects.filter(
                agent_uuid=property_obj.agent_uuid
            ).first()
            return bool(agent and agent.verified)

        if property_obj.company_uuid and property_obj.company_uuid != 'None':
            company = CompanyInformation.objects.filter(
                unique_company_id=property_obj.company_uuid
            ).first()
            return bool(company and company.verified)

        if property_obj.landlord_uuid and property_obj.landlord_uuid != 'None':
            from landlord.models import LandlordInformation
            landlord = LandlordInformation.objects.filter(
                landlord_uuid=property_obj.landlord_uuid
            ).first()
            return bool(landlord and landlord.verified)

    except Exception:
        pass
    return False


def _is_fully_complete(property_obj):
    """
    True if the listing has filled all the fields that matter most
    for a buyer/renter to make a decision.
    """
    return all([
        property_obj.bedrooms,
        property_obj.bathrooms,
        property_obj.location,
        property_obj.phone_number,
        property_obj.base_image,
    ])


def _count_media(property_obj):
    """Returns total image count (base image counts as 1)."""
    extra = property_obj.images.count()      # related formset images
    base  = 1 if property_obj.base_image else 0
    return base + extra


def _get_activity_counts(property_obj, property_type):
    """
    Returns (views, saves, inquiries) for a property.
    Imported locally to avoid circular imports.
    """
    try:       # adjust app label if different

        views     = PropertyViews.objects.filter(
            property_type=property_type,
            property_id=property_obj.pk
        ).count()

        saves     = WishlistStorageUnit.objects.filter(
            property_type=property_type,
            property_id=property_obj.pk
        ).count()

        inquiries = LeadInfo.objects.filter(
            property_type=property_type,
            property_intrested=property_obj.pk
        ).count()

        return views, saves, inquiries

    except Exception:
        return 0, 0, 0


# ── core calculation (always starts from zero) ────────────────────────────────

def _calculate_full_score(property_obj, property_type):
    """
    Calculates the complete listing score from scratch.
    Never reads the stored listing_score — so calling this twice
    produces the same result (idempotent).
    """
    points = 0

    # ── 1. Media density ─────────────────────────────────────────────
    media = _count_media(property_obj)
    if media >= 3:
        points += 10
    elif media >= 1:
        points += 5
    # 0 images → 0 points

    # ── 2. Description quality ───────────────────────────────────────
    desc_len = len(_get_description(property_obj, property_type))
    if desc_len >= 200:
        points += 10
    elif desc_len >= 50:
        points += 5
    # < 50 chars → 0 points

    # ── 3. Verified lister bonus ─────────────────────────────────────
    if _is_verified_lister(property_obj):
        points += 5

    # ── 4. Full completion bonus ──────────────────────────────────────
    if _is_fully_complete(property_obj):
        points += 5

    # ── 5. New listing boost (first 48 hours only) ────────────────────
    # Handled later via the age multiplier, but we give a flat +10 here
    # only at initial scoring (flag it via the caller).
    # Actually handled in score_new_listing() below.

    # ── 6. Activity ───────────────────────────────────────────────────
    views, saves, inquiries = _get_activity_counts(property_obj, property_type)

    if views >= 10:
        points += 10
    if saves >= 5:
        points += 10
    if inquiries >= 5:
        points += 10

    # ── 7. Age multiplier ─────────────────────────────────────────────
    age = timezone.now() - property_obj.listed_date

    if age <= timedelta(hours=48):
        points = int(points * 1.2)          # new listing boost
    elif age <= timedelta(days=7):
        pass                                 # baseline — no change
    elif age <= timedelta(days=30):
        points = int(points * 0.8)           # initial decay
    else:
        points = int(points * 0.5)           # old listing penalty

    # ── 8. Featured listing override ─────────────────────────────────
    if property_obj.featured_listings:
        points += 50

    return points


# ── public API ────────────────────────────────────────────────────────────────

def score_new_listing(property_obj, property_type):
    """
    Called ONCE right after a property is first saved.
    Includes the new-user / new-listing +10 boost.
    Saves the score back to the object.
    """
    points = _calculate_full_score(property_obj, property_type)

    # Extra +10 for brand-new listings (first time only)
    points += 10

    property_obj.listing_score = points
    property_obj.last_reset_date = timezone.now()
    property_obj.save(update_fields=['listing_score', 'last_reset_date'])

    return points


def refresh_activity_score(property_obj, property_type, force=False, save=True):
    """
    Recalculates the full score from scratch and follows a 24-hour gate.

    If save=False, the object is updated in memory but not saved to the DB.
    This is useful for bulk_update operations.
    """
    now     = timezone.now()
    elapsed = now - property_obj.last_reset_date

    # ── 24-hour gate ──────────────────────────────────────────────────
    if not force and elapsed < timedelta(hours=24):
        return property_obj.listing_score          # nothing to do

    points = _calculate_full_score(property_obj, property_type)

    property_obj.listing_score  = points
    property_obj.last_reset_date = now
    
    if save:
        property_obj.save(update_fields=['listing_score', 'last_reset_date'])

    return points




def get_inventory_count(agent, company=None, landlord=None):
    """
    Getting how many properties an agent/landlord have stored
    either listed/unlisted
    """
    if company:
        return(PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id).count()+
                PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id).count())
    elif agent:
        #Solo agent - only their own properties
        return(PropertyManagementRent.objects.filter(agent_uuid=agent.agent_uuid).count()+
                PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid).count())
    elif landlord:
        return(PropertyManagementRent.objects.filter(landlord_uuid=landlord.landlord_uuid).count()+
                PropertyManagementSale.objects.filter(landlord_uuid=landlord.landlord_uuid).count())
    return 0
def get_listing_count(agent, company=None, landlord=None):
    """
    How many properties are Currently LIVE
    """
    if company:
        return(
            PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id,is_listed=True).count()+
            PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id,is_listed=True).count()
        )
    elif agent:
        return(
            PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid,is_listed=True).count() + 
            PropertyManagementRent.objects.filter(agent_uuid=agent.agent_uuid,is_listed=True).count()
        )
    elif landlord:
        return(
            PropertyManagementSale.objects.filter(landlord_uuid=landlord.landlord_uuid,is_listed=True).count() + 
            PropertyManagementRent.objects.filter(landlord_uuid=landlord.landlord_uuid,is_listed=True).count()
        )
    return 0
def can_add_to_inventory(agent, company=None, landlord=None):
    """
    Can this agent/company/landlord store one more property?
    """
    
    if company and company.company_tier =='enterprise':
        return True, 'ok'
    
    if landlord:
        limit = landlord.inventory_slots
        used = get_inventory_count(None, None, landlord)
    else:
        limit=company.inventory_slots if company else agent.inventory_slot
        used=get_inventory_count(agent, company)
    
    if used >= limit:
        return False, f'Inventory full {used}/{limit} slots used. Upgrade to add more'
    return True,'ok'
def can_go_live(agent, company=None, landlord=None):
    """
    Can this agent/company/landlord make one more property live?
    """
    if company and company.company_tier == 'enterprise':
        return True, 'ok'
    
    if landlord:
        limit = landlord.listing_slots
        used = get_listing_count(None, None, landlord)
    else:
        limit= company.listing_slots if company else agent.listing_slots
        used= get_listing_count(agent, company)
    
    if used >= limit:
        return False, f'Listing limit reached ({used}/{limit} live) Unlist another property first or upgrade'
    return True, 'ok'

def get_agent_company(agent):
    """
    Returns CompanyInformation object if aent is in a company, else None
    """
    if not agent.company_uuid:
        return None
    try:
        return CompanyInformation.objects.get(unique_company_id=agent.company_uuid)
    except CompanyInformation.DoesNotExist:
        return None

def send_estate_email(subject, template_name, context, recipient_list):
    """
    Centralized utility to send HTML emails with a plain-text fallback.
    - subject: Email subject
    - template_name: Path to HTML template (e.g., 'emails/inquiry_notification.html')
    - context: Dictionary of data for the template
    - recipient_list: List of email addresses
    """
    try:
        # 1. Add common context (domain, protocol)
        if 'domain' not in context:
            # Try to get from request if provided in context, else from settings or hardcoded
            if 'request' in context:
                context['domain'] = context['request'].get_host()
                context['protocol'] = 'https' if context['request'].is_secure() else 'http'
            else:
                context['domain'] = 'estatewebng.com' if not settings.DEBUG else 'localhost:8000'
                context['protocol'] = 'https' if not settings.DEBUG else 'http'
        
        # 2. Render HTML
        html_content = render_to_string(template_name, context)
        
        # 3. Create plain-text fallback
        text_content = strip_tags(html_content)
        
        # 4. Create Email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        
        # 5. Send
        email.send(fail_silently=False)
        return True
    except Exception as e:
        ErrorLog.objects.create(traceback=f"Email Error ({subject}) to {recipient_list}: {str(e)}\n{traceback.format_exc()}")
        return False
