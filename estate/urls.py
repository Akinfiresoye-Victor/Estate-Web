'''Handles the Wesite routing'''
from django.urls import path
from . import views


app_name='customer'
urlpatterns = [
    path('properties/lease', views.rent_property, name="rent-property"),
    path('users/profile', views.user_profile, name="user-profile"),
    path('properties/sale', views.buy_property, name="buy-property"),
    path('property_view/sale/<property_id>/', views.view_property_on_sale, name="view-property-s"),
    path('property_view/rent/<property_id>/', views.view_property_on_lease, name="view-property-r"),
    path('users/profile/update/<user_id>/', views.update_profile, name="update-profile"),
    path('wishlist/toggle/rent/<property_id>/', views.toggle_wishlist_rent, name="toggle-wishlist-rent"),
    path('wishlist/toggle/sale/<property_id>/', views.toggle_wishlist_buy, name="toggle-wishlist-buy"),
    path('wishlist', views.wishlist, name="wishlist"),
    path('users/edit/password', views.change_password, name="change-password"),
    path('success', views.change_password_success, name="password-success"),
    path('users/profile/settings', views.profile_settings, name="settings"),
    path('users/account/deletion/', views.delete_account, name="delete-account"),
    path('form/inquiry/<property_type>/<property_id>', views.inquiry_form, name='inquiry-form'),
    path('review/<str:company_uuid>/', views.review_company, name='review-company'),
]


