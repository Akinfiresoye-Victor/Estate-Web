'''Handles the Wesite routing'''
from django.urls import path
from . import views


app_name='customer'
urlpatterns = [
    path('properties/lease', views.rent_property, name="rent-property"),
    path('users/profile', views.user_profile, name="user-profile"),
    path('properties/sale', views.buy_property, name="buy-property"),
    path('property_view/sale/<int:property_id>/', views.view_property_on_sale, name="view-property-s"),
    path('property_view/rent/<int:property_id>/', views.view_property_on_lease, name="view-property-r"),
    path('update_profile', views.update_profile, name="update-profile"),
    path('wishlist/toggle/rent/<int:property_id>/', views.toggle_wishlist_rent, name="toggle-wishlist-rent"),
    path('wishlist/toggle/sale/<int:property_id>/', views.toggle_wishlist_buy, name="toggle-wishlist-buy"),
    path('wishlist', views.wishlist, name="wishlist"),
    path('users/edit/password', views.change_password, name="change-password"),
    path('success', views.change_password_success, name="password-success"),
    path('users/profile/settings', views.profile_settings, name="settings"),
    path('users/account/deletion/', views.delete_account, name="delete-account"),
    path('form/inquiry/<str:property_type>/<int:property_id>', views.inquiry_form, name='inquiry-form'),
    path('review_company/<str:company_uuid>/', views.review_company, name='review-company'),
    path('review_agent/<str:agent_uuid>/', views.review_agent, name='review-agent'),
    path('report_listing/<int:property_id>/<str:property_type>', views.flag_listing, name='flag-listing'),
    path('compare/', views.compare_properties, name='compare'),
    path('compare/toggle/<str:property_type>/<int:property_id>/',views.toggle_compare, name='toggle-compare'),
    path('compare/clear/', views.clear_compare, name='clear-compare'),
    path('profile/agent/<agent_uuid>', views.agent_profile, name='agent-profile'),
    path('profile/company/<company_uuid>', views.company_profile, name='company-profile'),
    path('profile/landlord/<landlord_uuid>', views.view_landlord_profile, name='landlord-profile'),
]



