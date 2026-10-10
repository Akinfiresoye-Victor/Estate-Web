from collections import defaultdict
from decimal import Decimal
from django.db.models import Case, IntegerField, Sum, When, F
from .models import (
    PropertyInteraction,
    PropertyManagementSale,
    PropertyManagementRent,
    RecommendationData,
    RecommendedProperties,
)
from django.core.exceptions import ObjectDoesNotExist
import heapq
import logging
import time
from django.db import transaction


PROPERTY_MODELS = {
    'Sale': PropertyManagementSale,
    'Rent': PropertyManagementRent,
}


PRICE_FIELD = {'Sale': 'price', 'Rent': 'price_range'}

def log_interaction(user, property_type, property_id, action):
    """
    View - 5
    saved - 10
    inquire - 15
    hid - 10
    """
    if not user.is_authenticated:
        return
    PropertyInteraction.objects.create(
        user=user,
        property_type=property_type,
        property_id= property_id,
        action=action
    )
    


# How much each action is worth
INTERACTION_WEIGHTS = Case(
    When(action='view', then=5),
    When(action='save', then=10),
    When(action='inquire', then=15),
    When(action='recommend_click', then=1),   # must match the model's choice name
    When(action='hide', then=-40),
    default=0,
    output_field=IntegerField(),
)


def _interaction_scores(user):
    """Return {(property_type, property_id): total_score} for one user."""
    #Getting the score for each of the properties
    rows = (
        PropertyInteraction.objects
        .filter(user=user)
        .values('property_type', 'property_id')
        .annotate(total_score=Sum(INTERACTION_WEIGHTS))
    )
    #Returning a dictionary
    return {
        (r['property_type'], r['property_id']): r['total_score']
        for r in rows
    }


def recommendation_calculation(user):
    """Work out the user's taste for Sale and Rent, then save it."""
    scores = _interaction_scores(user)

    for ptype, Model in PROPERTY_MODELS.items():
        # Only the IDs this user touched for this property type
        ids = [pid for (t, pid) in scores if t == ptype]

        # Hidden or negative properties get weight 0, so they stop counting
        weights = {pid: max(scores[(ptype, pid)], 0) for pid in ids}

        props = Model.objects.filter(id__in=ids, is_listed=True).values(
            'id', 'bedrooms', 'bathrooms', 'state', 'property_category',
            property_price=F(PRICE_FIELD[ptype]),
        )

        total_w = Decimal('0')
        sum_price = Decimal('0')
        sum_beds = 0
        sum_baths = 0
        state_w = defaultdict(int)
        cat_w = defaultdict(int)

        for p in props:
            w = weights.get(p['id'], 0)
            if w == 0:
                continue

            total_w += w
            sum_price += (p['property_price'] or 0) * w
            sum_beds += (p['bedrooms'] or 0) * w
            sum_baths += (p['bathrooms'] or 0) * w

            if p['state']:
                state_w[p['state']] += w
            if p['property_category']:
                cat_w[p['property_category']] += w

        # No positive signals for this type: clear the old row
        if total_w == 0:
            RecommendationData.objects.filter(user=user, property_type=ptype).delete()
            continue
        
        top_3_states = heapq.nlargest(3, state_w, key=lambda state: state_w[state]) if state_w else []
        top_3_cat = heapq.nlargest(3, cat_w, key=lambda category: cat_w[category]) if cat_w else []
        RecommendationData.objects.update_or_create(
            user=user,
            property_type=ptype,
            defaults={
                'average_price': (sum_price / total_w).quantize(Decimal('0.01')),
                'average_beds': round(sum_beds / total_w),
                'average_bathrooms': round(sum_baths / total_w),
                'state_recomendations': top_3_states,
                'recomended_category': top_3_cat,
            },
        )





# def _check_price_difference(price: float, avg_price: float) ->bool:
#     """Return the percentage difference between price and average price for recommended pricing range."""
#     price_difference= abs(avg_price + (avg_price/2))
#     hi_price = avg_price + price_difference
#     lo_price = avg_price - price_difference
#     if lo_price <= price <= hi_price:
#         return True
#     else:
#         return False


# def _check_ammenities(bed: int, bath: int, avg_beds, avg_bathrooms)-> int:
#     bath_diff= abs(avg_bathrooms + (avg_bathrooms/2))
#     bed_diff= abs(avg_beds + (avg_beds/2))
    
#     hi_bath= avg_bathrooms + bath_diff
#     lo_bath= avg_bathrooms - bath_diff
    
#     hi_bed= avg_beds + bed_diff
#     lo_bed= avg_beds - bed_diff
#     score=0
#     if lo_bed <= bed <= hi_bed:
#         score +=2
        
#     if lo_bath <= bath <= hi_bath:
#         score +=2
#     return score



# def recommend_properties(user):
#     """DB operation to save the recomended properties for a user."""
#     try:
#         recommendation_data= RecommendationData.objects.filter(user=user).first()
#         properties_on_sale= PropertyManagementSale.objects.filter(is_listed=True)
#         properties_on_lease= PropertyManagementRent.objects.filter(is_listed=True)
#         if not recommendation_data:
#             return None
#         common_state= recommendation_data.state_recomendations
#         average_price= recommendation_data.average_price
#         average_beds= recommendation_data.average_beds
#         average_bathrooms= recommendation_data.average_bathrooms
#         recomended_category= recommendation_data.recomended_category
        
#         #Properties On Sale
#         for on_sale in properties_on_sale:
#             score= 0
#             if _check_price_difference(on_sale.price, average_price):
#                 score +=5
#             score += _check_ammenities(on_sale.bedrooms, on_sale.bathrooms, average_beds, average_bathrooms)

#             state_count= len(common_state)
#             if state_count == 0:
#                 score +=0
#             elif state_count == 1:
#                 if on_sale.state == common_state[0]:
#                     score +=10
#                 else:
#                     continue
#             elif state_count == 2:
#                 if on_sale.state == common_state[0]:
#                     score +=10
#                 elif on_sale.state == common_state[1]:
#                     score +=8
#                 else:
#                     continue
#             elif state_count == 3:
#                 if on_sale.state == common_state[0]:
#                     score +=10
#                 elif on_sale.state == common_state[1]:
#                     score +=8
#                 elif on_sale.state == common_state[2]:
#                     score +=6
#                 else:
#                     continue
#             else:
#                 score +=0
            
            
            
#             category_count= len(recomended_category)
#             if category_count == 0:
#                 score +=0
#             elif category_count == 1:
#                 if on_sale.property_category == recomended_category[0]:
#                     score +=2
#                 else:
#                     continue
#             elif category_count == 2:
#                 if on_sale.property_category == recomended_category[0]:
#                     score +=2
#                 elif on_sale.property_category == recomended_category[1]:
#                     score +=1
#                 else:
#                     continue
#             elif category_count == 3:
#                 if on_sale.property_category == recomended_category[0]:
#                     score +=2
#                 elif on_sale.property_category == recomended_category[1]:
#                     score +=1
#                 elif on_sale.property_category == recomended_category[2]:
#                     score +=0.5
#                 else:
#                     continue
#             else:
#                 score +=0
#             RecommendedProperties.objects.update_or_create(
#                 user= user,
#                 property_type= "Sale",
#                 defaults={
#                     'property_id': on_sale.pk,
#                     'recommendation_score': score
#                 }
#             )


#         #Properties on lease
#         for on_lease in properties_on_lease:
#             score= 0
#             if _check_price_difference(on_lease.price_range, average_price):
#                 score +=5
#             score += _check_ammenities(on_lease.bedrooms, on_lease.bathrooms, average_beds, average_bathrooms)

#             state_count= len(common_state)
#             if state_count == 0:
#                 score +=0
#             elif state_count == 1:
#                 if on_lease.state == common_state[0]:
#                     score +=10
#                 else:
#                     continue
#             elif state_count == 2:
#                 if on_lease.state == common_state[0]:
#                     score +=10
#                 elif on_lease.state == common_state[1]:
#                     score +=8
#                 else:
#                     continue
#             elif state_count == 3:
#                 if on_lease.state == common_state[0]:
#                     score +=10
#                 elif on_lease.state == common_state[1]:
#                     score +=8
#                 elif on_lease.state == common_state[2]:
#                     score +=6
#                 else:
#                     continue
#             else:
#                 score +=0
            
            
            
#             category_count= len(recomended_category)
#             if category_count == 0:
#                 score +=0
#             elif category_count == 1:
#                 if on_lease.property_category == recomended_category[0]:
#                     score +=2
#                 else:
#                     continue
#             elif category_count == 2:
#                 if on_lease.property_category == recomended_category[0]:
#                     score +=2
#                 elif on_lease.property_category == recomended_category[1]:
#                     score +=1
#                 else:
#                     continue
#             elif category_count == 3:
#                 if on_lease.property_category == recomended_category[0]:
#                     score +=2
#                 elif on_lease.property_category == recomended_category[1]:
#                     score +=1
#                 elif on_lease.property_category == recomended_category[2]:
#                     score +=0.5
#                 else:
#                     continue
#             else:
#                 score +=0
            
#             RecommendedProperties.objects.update_or_create(
#                 user= user,
#                 property_type= "Sale",
#                 defaults={
#                     'property_id': on_lease.pk,
#                     'recommendation_score': score
#                 }
#             )


#     except ObjectDoesNotExist:
#         return None






logger = logging.getLogger(__name__)

# ── Your scoring rules, in one place ───────────────────────────
PRICE_POINTS = 5
BED_POINTS = 2
BATH_POINTS = 2
STATE_POINTS = (10, 8, 6)          # 1st, 2nd, 3rd favourite state
CATEGORY_POINTS = (2, 1, 0.5)      # 1st, 2nd, 3rd favourite category
TOLERANCE = 0.5                    # "close enough" = within ±50% of the average
STORE_LIMIT = None                 # e.g. 500 to keep only the top 500 per user


def load_catalogue():
    """Load every live property ONCE, as light tuples (not full model objects)."""
    catalogue = {}
    for ptype, Model in PROPERTY_MODELS.items():
        catalogue[ptype] = list(
            Model.objects.filter(is_listed=True)
            .order_by('-listing_score', '-listed_date')   # ties will keep this order
            .values_list(
                'id', PRICE_FIELD[ptype], 'bedrooms', 'bathrooms',
                'state', 'property_category', 'listing_score',
            )
        )
    return catalogue


def _prepare_taste(rec):
    """Turn a RecommendationData row into plain numbers ONCE per user,
    so the scoring loop does no conversions or lookups."""
    avg_price = float(rec.average_price or 0)
    avg_beds = rec.average_beds or 0
    avg_baths = rec.average_bathrooms or 0
    states = (rec.state_recomendations or [])[:3]
    categories = (rec.recomended_category or [])[:3]

    return {
        'has_price': avg_price > 0,
        'price_lo': avg_price * (1 - TOLERANCE),
        'price_hi': avg_price * (1 + TOLERANCE),
        'has_beds': avg_beds > 0,
        'bed_lo': avg_beds * (1 - TOLERANCE),
        'bed_hi': avg_beds * (1 + TOLERANCE),
        'has_baths': avg_baths > 0,
        'bath_lo': avg_baths * (1 - TOLERANCE),
        'bath_hi': avg_baths * (1 + TOLERANCE),
        # {'Lagos': 10, 'Ogun': 8, 'Abuja': 6}: a dictionary lookup replaces the if/elif ladder
        'state_points': {s: STATE_POINTS[i] for i, s in enumerate(states)},
        'cat_points': {c: CATEGORY_POINTS[i] for i, c in enumerate(categories)},
    }


def _score_one(row, taste):
    _id, price, beds, baths, state, category, listing_score = row

    # Listing score only breaks ties: at most 0.20, always smaller than your smallest rule (0.5)
    score = min(listing_score or 0, 20) * 0.01

    if taste is None:               # no taste for this type: everything just ties
        return score

    if taste['has_price'] and price is not None and taste['price_lo'] <= float(price) <= taste['price_hi']:
        score += PRICE_POINTS
    if taste['has_beds'] and beds is not None and taste['bed_lo'] <= beds <= taste['bed_hi']:
        score += BED_POINTS
    if taste['has_baths'] and baths is not None and taste['bath_lo'] <= baths <= taste['bath_hi']:
        score += BATH_POINTS

    score += taste['state_points'].get(state, 0)          # 0 if not a favourite state
    score += taste['cat_points'].get(category, 0)         # 0 if not a favourite category
    return score


def score_catalogue(catalogue, tastes):
    """Score ALL properties for one user. Returns [(type, id, score), ...] best first."""
    scored = []
    for ptype, rows in catalogue.items():
        taste = tastes.get(ptype)
        for row in rows:
            scored.append((ptype, row[0], _score_one(row, taste)))

    # Python's sort is "stable": equal scores keep their earlier order,
    # which is already listing-score order from load_catalogue()
    scored.sort(key=lambda item: item[2], reverse=True)
    return scored


def save_recommendations(user_id, scored):
    if STORE_LIMIT:
        scored = scored[:STORE_LIMIT]

    new_rows = [
        RecommendedProperties(
            user_id=user_id,
            property_type=ptype,
            property_id=pid,
            recommendation_score=Decimal(f'{score:.2f}'),
        )
        for ptype, pid, score in scored
    ]

    with transaction.atomic():      # all or nothing: readers never see a half-built list
        RecommendedProperties.objects.filter(user_id=user_id).delete()
        RecommendedProperties.objects.bulk_create(new_rows, batch_size=1000)


def rebuild_all_recommendations(pause=0.0):
    """Score every live property for every user that has a taste profile."""
    catalogue = load_catalogue()                      # 2 queries total

    # All taste rows in ONE query, grouped by user
    tastes_by_user = defaultdict(dict)
    for rec in RecommendationData.objects.all().iterator(chunk_size=2000):
        tastes_by_user[rec.user_id][rec.property_type] = _prepare_taste(rec)

    rebuilt = failed = 0
    for user_id, tastes in tastes_by_user.items():
        try:
            save_recommendations(user_id, score_catalogue(catalogue, tastes))
            rebuilt += 1
        except Exception:
            failed += 1
            logger.exception('Recommendation rebuild failed for user %s', user_id)
        if pause:
            time.sleep(pause)                         # be gentle on the database

    # Users who lost all their taste data: clear stale rows (the page falls back to default order)
    cleared, _ = (
        RecommendedProperties.objects
        .exclude(user__in=RecommendationData.objects.values('user'))
        .delete()
    )
    return rebuilt, failed, cleared