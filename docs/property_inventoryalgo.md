# Estate Web — Inventory & Listing Slot System
## Implementation Algorithm

---

## 1. Core Concepts (Read This First)

```
PROPERTY STATES:
┌─────────────┐     toggle ON      ┌─────────────┐     delete     ┌──────────────┐
│  INVENTORY  │ ─────────────────► │   LISTED    │ ─────────────► │   DELETED    │
│  (private)  │ ◄───────────────── │  (public)   │                │  (gone)      │
└─────────────┘     toggle OFF     └─────────────┘                └──────────────┘

AGENT TYPES:
- Solo Agent     → has personal slots, posts independently
- Company Agent  → no personal slots, draws from company pool

SLOT TYPES:
- Inventory Slot → how many properties can be STORED (listed + unlisted combined)
- Listing Slot   → how many can be PUBLICLY VISIBLE at once
- Listing Slots are always SMALLER than Inventory Slots
```

---

## 2. Database Changes

### 2.1 Add `is_listed` to both property models

```python
# Add to PropertyManagementSale and PropertyManagementRent
is_listed = models.BooleanField(default=False)
# False = stored in inventory, not visible to public
# True  = live on the platform, visible to buyers/renters
```

### 2.2 Solo Agent Slots — add to `AgentInformation`

```python
# Only used when agent has NO company (company_uuid is None/empty)
inventory_slots = models.IntegerField(default=10)
listing_slots   = models.IntegerField(default=6)
```

### 2.3 Company Tiers — add to `CompanyInformation`

```python
COMPANY_TIER = [
    ('starter',    'Starter'),     # 50 inventory / 30 live
    ('growth',     'Growth'),      # 200 inventory / 120 live
    ('enterprise', 'Enterprise'),  # unlimited
]

company_tier      = models.CharField(choices=COMPANY_TIER, default='starter')
inventory_slots   = models.IntegerField(default=50)
listing_slots     = models.IntegerField(default=30)
```

### 2.4 Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 3. Slot Logic Helpers

> These are utility functions. Put them in a `utils.py` or `helpers.py` file
> inside your core app. Import them into views.

### 3.1 Get current usage counts

```python
def get_inventory_count(agent, company=None):
    """
    How many properties does this agent/company currently have stored?
    Counts BOTH listed and unlisted — anything in inventory.
    """
    if company:
        # All properties posted by any agent in this company
        return (
            PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id).count() +
            PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id).count()
        )
    else:
        # Solo agent — only their own properties
        return (
            PropertyManagementSale.objects.filter(user_id=agent.user_id).count() +
            PropertyManagementRent.objects.filter(user_id=agent.user_id).count()
        )


def get_listing_count(agent, company=None):
    """
    How many properties are currently LIVE (is_listed=True)?
    """
    if company:
        return (
            PropertyManagementSale.objects.filter(company_uuid=company.unique_company_id, is_listed=True).count() +
            PropertyManagementRent.objects.filter(company_uuid=company.unique_company_id, is_listed=True).count()
        )
    else:
        return (
            PropertyManagementSale.objects.filter(user_id=agent.user_id, is_listed=True).count() +
            PropertyManagementRent.objects.filter(user_id=agent.user_id, is_listed=True).count()
        )
```

### 3.2 Check if slots are available

```python
def can_add_to_inventory(agent, company=None):
    """
    Can this agent/company store one more property?
    Returns (bool, reason_string)
    """
    if company and company.company_tier == 'enterprise':
        return True, 'ok'

    limit = company.inventory_slots if company else agent.inventory_slots
    used  = get_inventory_count(agent, company)

    if used >= limit:
        return False, f'Inventory full ({used}/{limit} slots used). Upgrade to add more.'
    return True, 'ok'


def can_go_live(agent, company=None):
    """
    Can this agent/company make one more property live?
    Returns (bool, reason_string)
    """
    if company and company.company_tier == 'enterprise':
        return True, 'ok'

    limit = company.listing_slots if company else agent.listing_slots
    used  = get_listing_count(agent, company)

    if used >= limit:
        return False, f'Listing limit reached ({used}/{limit} live). Unlist another property first or upgrade.'
    return True, 'ok'
```

### 3.3 Resolve which company an agent belongs to

```python
def get_agent_company(agent):
    """
    Returns CompanyInformation object if agent is in a company, else None.
    """
    if not agent.company_uuid:
        return None
    try:
        return CompanyInformation.objects.get(unique_company_id=agent.company_uuid)
    except CompanyInformation.DoesNotExist:
        return None
```

---

## 4. View Changes

### 4.1 sell_property / lease_property (creating a new property)

```
ALGORITHM:
1. Check user is authenticated + role is agent or company
2. Get agent's AgentInformation
3. Get agent's company (if any)
4. Call can_add_to_inventory(agent, company)
   ├── If False → show error message, do not save, redirect back
   └── If True  → continue
5. Save the property with is_listed=False (goes to inventory, NOT live)
6. Set company_uuid on the property if agent belongs to a company
7. Call score_new_listing() as before
8. Redirect to inventory dashboard with success message
```

```python
def sell_property(request):
    if request.method == 'POST':
        agent   = AgentInformation.objects.get(user_id=request.user.id)
        company = get_agent_company(agent)

        allowed, reason = can_add_to_inventory(agent, company)
        if not allowed:
            messages.error(request, reason)
            return redirect('listings')

        form = SellPropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop              = form.save(commit=False)
            prop.user_id      = request.user.id
            prop.is_listed    = False  # ← goes to inventory, not live yet
            prop.agent_uuid   = agent.agent_uuid
            prop.company_uuid = company.unique_company_id if company else None
            prop.save()
            score_new_listing(prop, 'Sale')
            messages.success(request, 'Property saved to inventory. Toggle it live when ready.')
            return redirect('listings')
```

### 4.2 toggle_listing (new view)

```
ALGORITHM:
1. Get the property by ID
2. Confirm the requesting user owns this property (security check)
3. If currently is_listed=True (going to unlist):
   ├── Set is_listed=False
   └── Save → done, no slot check needed (freeing a slot)

4. If currently is_listed=False (going to list/make live):
   ├── Get agent + company
   ├── Call can_go_live(agent, company)
   │   ├── If False → return error (slot limit reached)
   │   └── If True  → set is_listed=True, save
   └── Return success
```

```python
def toggle_listing(request, property_id, property_type):
    """
    Toggles a property between inventory (private) and listed (public).
    property_type: 'sale' or 'rent'
    Supports AJAX: returns JSON if X-Requested-With header present.
    """
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    Model = PropertyManagementSale if property_type == 'sale' else PropertyManagementRent

    try:
        prop = Model.objects.get(pk=property_id, user_id=request.user.id)
    except Model.DoesNotExist:
        if is_ajax:
            return JsonResponse({'error': 'Not found'}, status=404)
        messages.error(request, 'Property not found.')
        return redirect('listings')

    if prop.is_listed:
        # ── UNLIST: always allowed, just flip the flag ──
        prop.is_listed = False
        prop.save(update_fields=['is_listed'])
        msg = 'Property moved back to inventory.'
        if is_ajax:
            return JsonResponse({'is_listed': False, 'message': msg})
        messages.success(request, msg)

    else:
        # ── LIST: check slot availability first ──
        agent   = AgentInformation.objects.get(user_id=request.user.id)
        company = get_agent_company(agent)

        allowed, reason = can_go_live(agent, company)
        if not allowed:
            if is_ajax:
                return JsonResponse({'error': reason}, status=403)
            messages.error(request, reason)
            return redirect('listings')

        prop.is_listed = True
        prop.save(update_fields=['is_listed'])
        msg = 'Property is now live on the platform.'
        if is_ajax:
            return JsonResponse({'is_listed': True, 'message': msg})
        messages.success(request, msg)

    return redirect('listings')
```

### 4.3 buy_property / rent_property (public listing pages)

```
Change the queryset filter to only show is_listed=True:
```

```python
# Before:
sale_qs = PropertyManagementSale.objects.all()

# After:
sale_qs = PropertyManagementSale.objects.filter(is_listed=True)
```

### 4.4 manage_listings / inventory view (agent sees everything)

```
This view shows ALL properties regardless of is_listed.
No filter on is_listed here — agents need to see their full inventory.
```

```python
def manage_listings(request):
    agent = AgentInformation.objects.get(user_id=request.user.id)
    company = get_agent_company(agent)

    # Show everything — listed AND unlisted
    sale_props = PropertyManagementSale.objects.filter(user_id=request.user.id)
    rent_props = PropertyManagementRent.objects.filter(user_id=request.user.id)

    # Slot counter for the UI
    inv_used  = get_inventory_count(agent, company)
    live_used = get_listing_count(agent, company)

    if company and company.company_tier == 'enterprise':
        inv_limit  = '∞'
        live_limit = '∞'
    elif company:
        inv_limit  = company.inventory_slots
        live_limit = company.listing_slots
    else:
        inv_limit  = agent.inventory_slots
        live_limit = agent.listing_slots

    context = {
        'sale_props':  sale_props,
        'rent_props':  rent_props,
        'inv_used':    inv_used,
        'inv_limit':   inv_limit,
        'live_used':   live_used,
        'live_limit':  live_limit,
    }
    return render(request, 'estate/manage_listings.html', context)
```

---

## 5. URL to Add

```python
# In your core urls.py
path('toggle_listing/<str:property_type>/<int:property_id>/',
     views.toggle_listing,
     name='toggle-listing'),
```

---

## 6. Inventory Dashboard UI — What to Show

```
┌─────────────────────────────────────────────────────────┐
│  SLOT COUNTER BAR (top of manage_listings page)         │
│                                                         │
│  Inventory:  ████████░░  8 / 10 used                   │
│  Live:       ████░░░░░░  4 / 6 used                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  PROPERTY ROW                                           │
│                                                         │
│  [Image]  3-Bed Flat, Lekki       ₦2,500,000           │
│           Residential · Lagos                           │
│                                                         │
│  Status:  ● LIVE    [Toggle OFF]  [Edit]  [Delete]     │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│                                                         │
│  [Image]  Office Space, VI         ₦800,000/mo          │
│           Commercial · Lagos                            │
│                                                         │
│  Status:  ○ STORED  [Go Live]     [Edit]  [Delete]     │
└─────────────────────────────────────────────────────────┘
```

**Toggle button logic on the UI:**
- If `is_listed=True` → show green "LIVE" badge + "Unlist" button
- If `is_listed=False` → show grey "STORED" badge + "Go Live" button
- If live slots are full → "Go Live" button is disabled + tooltip "Upgrade to list more"

---

## 7. Build Order (Do This Sequence)

```
Step 1 → Add is_listed field to both property models
Step 2 → Add slot fields to AgentInformation + CompanyInformation
Step 3 → Run migrations
Step 4 → Write the helper functions (utils.py)
Step 5 → Update sell_property + lease_property views
Step 6 → Update buy_property + rent_property queryset filter
Step 7 → Write toggle_listing view
Step 8 → Add toggle_listing URL
Step 9 → Update manage_listings view (context with slot counters)
Step 10 → Build the inventory dashboard UI (manage_listings.html)
Step 11 → Add slot counter bar + toggle buttons to the HTML
Step 12 → Test the full flow:
           → Create property → lands in inventory (not public)
           → Toggle live → appears on buy/rent page
           → Toggle off → disappears from public, stays in inventory
           → Delete → gone permanently
Step 13 → (Later) Build upgrade/payment flow for extra slots
```

---

## 8. Edge Cases to Handle

| Situation | What to do |
|-----------|-----------|
| Agent leaves company | Their properties stay, `company_uuid` on property is preserved, slot count stays with company |
| Company downgrades tier | Do NOT auto-unlist. Lock them from listing NEW properties until they're within limits |
| Agent has is_listed=True properties, then joins a company | Their existing live properties stay live. Future listings draw from company pool |
| Property gets deleted while listed | Just delete — slot frees itself automatically since count is calculated live from DB |
| Enterprise company | Skip all slot checks entirely (`company_tier == 'enterprise'`) |
| Solo agent joins company | Their personal slots become irrelevant. Company slots now apply going forward |

---

## 9. Slot Defaults Summary

| Account Type | Inventory | Live Listings |
|---|---|---|
| Solo Agent (free) | 10 | 6 |
| Solo Agent (paid upgrade) | 10 + purchased | 6 + purchased |
| Company — Starter | 50 | 30 |
| Company — Growth | 200 | 120 |
| Company — Enterprise | ∞ | ∞ |
| Company Agent | No personal limit — uses company pool | ← same |