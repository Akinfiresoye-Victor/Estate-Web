# estate/migrations/000X_auto_YYYYMMDD_HHMM.py (your newly created file)
from django.db import migrations
from decimal import Decimal, InvalidOperation # Import these for conversion

def clean_price_data(apps, schema_editor):
    PropertyManagementSale = apps.get_model('estate', 'PropertyManagementSale')
    # Assuming you also changed PropertyManagementRent's price_range field
    PropertyManagementRent = apps.get_model('estate', 'PropertyManagementRent')

    # Clean PropertyManagementSale.price
    for sale_obj in PropertyManagementSale.objects.all():
        if sale_obj.price is None or sale_obj.price.strip() == '':
            sale_obj.price = None # Set to None for null=True, or Decimal('0.00')
        else:
            try:
                # Remove currency symbols (like ₦), commas, and extra spaces
                clean_value = sale_obj.price.replace('₦', '').replace(',', '').strip()
                sale_obj.price = Decimal(clean_value)
            except InvalidOperation:
                # If conversion still fails (e.g., "N/A", "Contact for price"),
                # set to None or a default value like Decimal('0.00')
                print(f"Warning: Could not convert sale price '{sale_obj.price}'. Setting to None.")
                sale_obj.price = None
        sale_obj.save(update_fields=['price']) # Save only the changed field

    # Clean PropertyManagementRent.price_range (if applicable)
    for rent_obj in PropertyManagementRent.objects.all():
        if rent_obj.price_range is None or rent_obj.price_range.strip() == '':
            rent_obj.price_range = None # Or Decimal('0.00')
        else:
            try:
                clean_value = rent_obj.price_range.replace('₦', '').replace(',', '').strip()
                rent_obj.price_range = Decimal(clean_value)
            except InvalidOperation:
                print(f"Warning: Could not convert rent price range '{rent_obj.price_range}'. Setting to None.")
                rent_obj.price_range = None
        rent_obj.save(update_fields=['price_range'])


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0020_alter_propertymanagementrent_price_range_and_more'), # Replace with the actual name of the previous migration file
    ]

    operations = [
        migrations.RunPython(clean_price_data, reverse_code=migrations.RunPython.noop),
    ]