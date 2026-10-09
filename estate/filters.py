import django_filters
from django import forms
from django_filters import NumberFilter

from core.models import PropertyManagementRent, PropertyManagementSale


class PropertyRentFilter(django_filters.FilterSet):
    start_price = NumberFilter(
        field_name='price_range',
        lookup_expr='gte',
        label='Minimum price',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'inputmode': 'numeric',
            'min': '0',
            'placeholder': '₦ Minimum',
        }),
    )
    end_price = NumberFilter(
        field_name='price_range',
        lookup_expr='lte',
        label='Maximum price',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'inputmode': 'numeric',
            'min': '0',
            'placeholder': '₦ Maximum',
        }),
    )

    class Meta:
        model = PropertyManagementRent
        fields = ['property_category', 'state', 'rent_rate']
        widgets = {
            'property_category': forms.Select(attrs={'class': 'form-select'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'rent_rate': forms.Select(attrs={'class': 'form-select'}),
        }


class PropertySaleFilter(django_filters.FilterSet):
    start_price=NumberFilter(field_name='price', lookup_expr='gte',label='Minimum Price Range')
    end_price=NumberFilter(field_name='price', lookup_expr='lte',label='Maximum Price Range')
    class Meta:
        model=PropertyManagementSale
        fields=['property_category','state']
