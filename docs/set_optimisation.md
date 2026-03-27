# Using `set` to Optimize Estate Web — Quick Reference

## What is a `set` and why does it matter?

A `set` is a Python data structure that holds **unique values** and lets you check
membership in **O(1) time** — meaning the check is equally fast whether the set has
10 items or 10,000.

A plain Python **list** checks one by one (O(n)) — the bigger the list, the slower it gets.

**Simple analogy:**
- A **list** is like a paper guest list — you read it line by line from top to bottom.
- A **set** is like a bouncer who has every name memorized — instant check, every time.

---

## The Core Pattern

Instead of building a list of objects and looping through them:

```python
# SLOW — list scan, full objects fetched from DB
viewers = []
for v in PropertyViews.objects.filter(...):
    viewers.append(v.user_id)

if user_id in viewers:   # O(n) check
    ...
```

Fetch only the column you need and store it in a set:

```python
# FAST — one query, one column, O(1) check
viewer_ids = set(
    PropertyViews.objects.filter(...)
    .values_list('user_id', flat=True)
)

if user_id in viewer_ids:   # O(1) check
    ...
```

### Why `values_list('field', flat=True)`?
- Returns only that one column instead of full model objects
- `flat=True` gives a clean list like `[12, 45, 88]` instead of tuples `[(12,), (45,), (88,)]`
- Less data transferred from the database = faster query

---

## All Places to Use `set` in Estate Web

### 1. Wishlist heart icon — `buy_property` / `rent_property` views
Check which properties a user has wishlisted, once, before the loop.

```python
wishlist_ids = set(
    WishlistStorageUnit.objects.filter(user_id=request.user.id, property_type='Sale')
    .values_list('property_id', flat=True)
)
# In template: {% if property.id in wishlist_ids %}
```

---

### 2. Property view tracking — `property_view_count`
Check if a user has already viewed a property before creating a new record.

```python
all_views = set(
    PropertyViews.objects.filter(property_type=property_type, property_id=property_id)
    .values_list('user_id', flat=True)
)

if users_id not in all_views:
    PropertyViews.objects.create(
        user_id=users_id,
        property_type=property_type,
        property_id=property_id,
        uuid=users_uuid
    )
    # Note: .create() already saves — no need for .save() after it
```

---

### 3. Live/stored badges — listings/inventory page
Check which properties are currently listed, once, before rendering cards.

```python
listed_ids = set(
    PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid, is_listed=True)
    .values_list('id', flat=True)
)
# In template: {% if property.id in listed_ids %}
```

---

### 4. Slot check — `toggle_listing` view
Before toggling a property live, verify the agent hasn't hit their listing slot limit.

```python
active_listed = set(
    PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid, is_listed=True)
    .values_list('id', flat=True)
)

if len(active_listed) >= agent.listing_slots and property_id not in active_listed:
    return JsonResponse({'error': 'Listing slot limit reached'}, status=400)
```

---

### 5. Company team membership — `manage_company`
Check which agents belong to a company without re-querying per agent.

```python
team_uuids = set(
    AgentInformation.objects.filter(company_uuid=company.unique_company_id)
    .values_list('agent_uuid', flat=True)
)
```

---

### 6. Find Talents — exclude current team members
Exclude agents already on the company team from the talent search results.

```python
team_uuids = set(
    AgentInformation.objects.filter(company_uuid=company.unique_company_id)
    .values_list('agent_uuid', flat=True)
)

available_agents = AgentInformation.objects.exclude(agent_uuid__in=team_uuids)
```

---

### 7. State/location filter dropdown — deduplicate values
Remove duplicate state names for the filter dropdown without using SQL DISTINCT.

```python
states = sorted(set(
    PropertyManagementSale.objects.filter(is_listed=True)
    .values_list('state', flat=True)
))
```

---

### 8. Score refresh — `refresh_scores` management command
Skip properties that have already been refreshed today.

```python
already_refreshed = set(
    PropertyManagementSale.objects.filter(last_reset_date=today)
    .values_list('id', flat=True)
)

for prop in all_properties:
    if prop.id not in already_refreshed:
        refresh_activity_score(prop, 'Sale')
```

---

### 9. Agent analytics — check which categories are used
Check which property categories an agent has used without multiple filter calls.

```python
categories_used = set(
    PropertyManagementSale.objects.filter(agent_uuid=agent.agent_uuid)
    .values_list('property_category', flat=True)
)

has_residential = 'Residential' in categories_used
has_commercial = 'Commercial' in categories_used
```

---

## Quick Performance Reference

| Scenario | Before | After |
|---|---|---|
| User has 50 wishlisted, page shows 20 listings | 50 × 20 = 1,000 comparisons | 20 × O(1) = 20 comparisons |
| DB columns fetched per query | All fields (full object) | 1 column only |
| Duplicate filter dropdown values | Extra SQL or Python logic | `set()` removes them automatically |

---

## The Signal to Use a `set`

> **Any time you find yourself doing a membership check (`is this ID in this collection?`)
> inside a loop — whether that's a Python `for` loop or a Django template `{% for %}` —
> that's your signal to pull the collection into a `set` once before the loop starts.**