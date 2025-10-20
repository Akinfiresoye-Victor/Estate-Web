import django_filters
from django_filters import DateFilter, NumberFilter




from .models import PropertyManagementRent, PropertyManagementSale

class PropertyRentFilter(django_filters.FilterSet):
    start_price=NumberFilter(field_name='price_range', lookup_expr='gte', label='Minimum Price Range')
    end_price=NumberFilter(field_name='price_range', lookup_expr='lte',label='Maximum Price Range')
    class Meta:
        model=PropertyManagementRent
        fields=['house_type','state', 'available']
        
        
class PropertySaleFilter(django_filters.FilterSet):
    start_price=NumberFilter(field_name='price', lookup_expr='gte',label='Minimum Price Range')
    end_price=NumberFilter(field_name='price', lookup_expr='lte',label='Maximum Price Range')
    class Meta:
        model=PropertyManagementSale
        fields=['house_type','state', 'available']