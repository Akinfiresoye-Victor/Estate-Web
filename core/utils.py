from django.utils import timezone
from datetime import timedelta
from agents.models import AgentAnalytics
from core.models import PropertyViews
from companies.models import SessionId
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from estate.models import LeadInfo




def monthly_change(current_value, average_value):
    """Calculate percentage change from average"""
    if average_value == 0:
        return 0 if current_value == 0 else 100
    change = ((current_value - average_value) / average_value) * 100
    return round(change, 2)


def engagement_rate(total_likes, avg_property_views, avg_profile_views, rating_score):
    """
    Calculate engagement rate based on:
    - Total property likes
    - Average property views
    - Average profile views
    - Rating score (rating * review_count)
    """
    if avg_property_views == 0 and avg_profile_views == 0:
        return 0.0
    
    # Weighted engagement calculation
    like_weight = 0.4
    view_weight = 0.3
    profile_weight = 0.2
    rating_weight = 0.1
    
    # Normalize values
    like_score = min(total_likes / max(1, avg_property_views / 10), 100) * like_weight
    view_score = min(avg_property_views / 10, 100) * view_weight
    profile_score = min(avg_profile_views / 5, 100) * profile_weight
    rating_score_normalized = min(rating_score * 2, 100) * rating_weight
    
    total_engagement = like_score + view_score + profile_score + rating_score_normalized
    
    return round(total_engagement, 2)


def reset_button(analytics, agent_uuid, lease_views, sale_views):
    """Reset monthly tracking if 30 days have passed"""
    from core.models import PropertyManagementRent, PropertyManagementSale
    
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


def reset_button(analytics, company_uuid, lease_views, sale_views):
    """
    Reset monthly tracking every 30 days
    
    Plain English:
    Every 30 days:
    1. Calculate new averages: (old_average + this_month) ÷ 2
    2. Reset current counters to 0
    3. Start tracking next month
    
    Example:
    - Month 1: 150 views → Average = 150
    - Month 2: 200 views → New Average = (150 + 200) ÷ 2 = 175
    - Month 3: Counter resets, starts from 0 again
    """

    
    current_time = timezone.now()
    time_difference = current_time - analytics.last_reset_date
    
    if time_difference >= timedelta(days=30):
        # Calculate rolling averages
        analytics.average_profile_views = (analytics.profile_views + analytics.average_profile_views) // 2
        analytics.average_lease_views = (lease_views + analytics.average_lease_views) // 2
        analytics.average_sale_views = (sale_views + analytics.average_sale_views) // 2
        
        # Reset current month counters
        analytics.profile_views = 0
        analytics.property_views_l = 0
        analytics.property_views_s = 0
        analytics.last_reset_date = current_time
        
        analytics.save()
        
        # Clean up old tracking data
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