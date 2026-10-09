from collections import defaultdict
from decimal import Decimal
from django.db.models import Case, IntegerField, Sum, When
from .models import (
    PropertyInteraction,
    PropertyManagementSale,
    PropertyManagementRent,
    ReccomendationData,
)


PROPERTY_MODELS = {
    'Sale': PropertyManagementSale,
    'Rent': PropertyManagementRent,
}


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
            'id', 'price', 'bedrooms', 'bathrooms', 'state', 'property_category'
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
            sum_price += (p['price'] or 0) * w
            sum_beds += (p['bedrooms'] or 0) * w
            sum_baths += (p['bathrooms'] or 0) * w

            if p['state']:
                state_w[p['state']] += w
            if p['property_category']:
                cat_w[p['property_category']] += w

        # No positive signals for this type: clear the old row
        if total_w == 0:
            ReccomendationData.objects.filter(user=user, property_type=ptype).delete()
            continue

        ReccomendationData.objects.update_or_create(
            user=user,
            property_type=ptype,
            defaults={
                'average_price': (sum_price / total_w).quantize(Decimal('0.01')),
                'average_beds': round(sum_beds / total_w),
                'average_bathrooms': round(sum_baths / total_w),
                'state_recomendation': max(state_w, key=state_w.get) if state_w else None,
                'recomended_category': max(cat_w, key=cat_w.get) if cat_w else None,
            },
        )