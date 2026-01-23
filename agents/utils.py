from django.utils import timezone
from datetime import timedelta
from .models import AgentAnalytics


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