import django_filters
from django_filters import NumberFilter




from core.models import PropertyManagementRent, PropertyManagementSale

class PropertyRentFilter(django_filters.FilterSet):
    start_price=NumberFilter(field_name='price_range', lookup_expr='gte', label='Minimum Price Range')
    end_price=NumberFilter(field_name='price_range', lookup_expr='lte',label='Maximum Price Range')
    class Meta:
        model=PropertyManagementRent
        fields=['property_category','state']
        
        
class PropertySaleFilter(django_filters.FilterSet):
    start_price=NumberFilter(field_name='price', lookup_expr='gte',label='Minimum Price Range')
    end_price=NumberFilter(field_name='price', lookup_expr='lte',label='Maximum Price Range')
    class Meta:
        model=PropertyManagementSale
        fields=['property_category','state']