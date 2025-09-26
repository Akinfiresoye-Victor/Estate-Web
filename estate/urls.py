'''Handles the Wesite routing'''


from django.urls import path
from . import views


urlpatterns = [
    path('', views.welcome_page, name="welcome-page"),
    path('rent_prop', views.rent_property, name="rent-prop"),
    path('user_profile', views.user_profile, name="user-profile"),
    path('sell_property', views.sell_property, name="sell-property"),
    path('lease_property', views.lease_property, name="lease-property"),
    path('buy_property', views.buy_property, name="buy-property"),
    path('search_property', views.search_property, name="search-property"),
    path('update_property/<property_id>', views.update_property_rent, name="update-property"),
    path('update_property_s/<property_id>', views.update_property_sale, name="update-property-s"),
    path('my_listings', views.listed_properties, name="my-listings"),
    path('view-property_s/<property_id>', views.view_property_on_sale, name="view-property-s"),
    path('view-property_r/<property_id>', views.view_property_on_lease, name="view-property-r"),
    path('delete-property_r/<property_id>', views.delete_property_on_lease, name="delete-property-r"),
    path('delete-property_s/<property_id>', views.delete_property_on_sale, name="delete-property-s"),
    path('update-profile/<user_id>', views.update_profile, name="update-profile"),
    path('whilist_rent/<property_id>', views.toggle_wishlist_rent, name="toggle-wishlist-rent"),
    path('whilist_buy/<property_id>', views.toggle_wishlist_buy, name="toggle-wishlist-buy"),
    path('whilist', views.wishlist, name="wishlist"),
    path('edit_password', views.change_password, name="change-password"),
    path('edit_password_success', views.change_password_success, name="password-success"),
    path('settings', views.settings, name="settings"),
    path('delete_account', views.delete_account, name="delete-account"),
    path('best_deals_rent', views.best_deals_on_lease, name="best-deals-rent"),
    path('best_deals_sale', views.best_deals_on_sale, name="best-deals-sale"),
]
