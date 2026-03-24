from django.db import migrations


# ── Data to seed ──────────────────────────────────────────────────────────────

PROPERTY_FOCUS_OPTIONS = [
    "Residential Properties",
    "Commercial Properties",
    "Land & Plots",
    "Short-Let / Serviced Apartments",
    "Luxury Properties",
    "Affordable Housing",
    "Mixed-Use Developments",
    "Industrial & Warehousing",
    "Property Management",
    "Real Estate Investment",
]

PARTNERSHIP_GOAL_OPTIONS = [
    "Increased Visibility & Leads",
    "Verified Partner Badge",
    "Discounted Listing Fees",
    "Early Access to New Features",
    "Analytics & Market Data Tools",
    "Priority Customer Support",
    "Influence Product Direction",
    "Local Market Dominance",
    "Featured Property Placements",
    "Long-Term Collaboration Opportunities",
]


# ── Forward: insert rows ──────────────────────────────────────────────────────

def seed_data(apps, schema_editor):
    PropertyFocus   = apps.get_model("core", "PropertyFocus")
    PartnershipGoal = apps.get_model("core", "PartnershipGoal")

    for name in PROPERTY_FOCUS_OPTIONS:
        PropertyFocus.objects.get_or_create(name=name)

    for name in PARTNERSHIP_GOAL_OPTIONS:
        PartnershipGoal.objects.get_or_create(name=name)


# ── Reverse: delete the seeded rows ──────────────────────────────────────────

def unseed_data(apps, schema_editor):
    PropertyFocus   = apps.get_model("core", "PropertyFocus")
    PartnershipGoal = apps.get_model("core", "PartnershipGoal")

    PropertyFocus.objects.filter(name__in=PROPERTY_FOCUS_OPTIONS).delete()
    PartnershipGoal.objects.filter(name__in=PARTNERSHIP_GOAL_OPTIONS).delete()


# ── Migration class ───────────────────────────────────────────────────────────

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0040_partnershipgoal_propertyfocus_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=unseed_data),
    ]

