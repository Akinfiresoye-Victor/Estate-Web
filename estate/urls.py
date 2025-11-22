'''Handles the Wesite routing'''
from django.urls import path
from . import views


app_name='customer'
urlpatterns = [
    path('rent_prop', views.rent_property, name="rent-prop"),
    path('user_profile/', views.user_profile, name="user-profile"),
    path('buy_property/', views.buy_property, name="buy-property"),
    path('view-property_s/<property_id>/', views.view_property_on_sale, name="view-property-s"),
    path('view-property_r/<property_id>/', views.view_property_on_lease, name="view-property-r"),
    path('update-profile/<user_id>/', views.update_profile, name="update-profile"),
    path('whilist_rent/<property_id>/', views.toggle_wishlist_rent, name="toggle-wishlist-rent"),
    path('whilist_buy/<property_id>/', views.toggle_wishlist_buy, name="toggle-wishlist-buy"),
    path('whilist/', views.wishlist, name="wishlist"),
    path('edit_password/', views.change_password, name="change-password"),
    path('edit_password_success/', views.change_password_success, name="password-success"),
    path('settings/', views.profile_settings, name="settings"),
    path('delete_account/', views.delete_account, name="delete-account"),
    path('inquiry_form_r/<property_id>', views.inquiry_form_rent, name='inquiry-form-r'),
    path('inquiry_form_s/<property_id>', views.inquiry_form_sale, name='inquiry-form-s')
]


