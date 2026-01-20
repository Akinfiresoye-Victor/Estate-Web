from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('about/', views.about_page, name='about'),
    path('feedback/', views.feedbacks, name='feedback'),
    path('delete-property_r/<property_id>/', views.delete_property_on_lease, name="delete-property-r"),
    path('delete-property_s/<property_id>/', views.delete_property_on_sale, name="delete-property-s"),
    path('update_property/<property_id>/', views.update_property_rent, name="update-property"),
    path('update_property_s/<property_id>/', views.update_property_sale, name="update-property-s"),
    path('sell_property/', views.sell_property, name="sell-property"),
    path('lease_property/', views.lease_property, name="lease-property"),
    path('latest_news/', views.articles, name='articles'),
    path('estateweb/partners/', views.partner_with_us, name="partner-with-us"),
    path('add_schedule', views.add_schedule, name="add-schedule"),
    path('schedule_detail/<appt_uuid>', views.appointment_detail, name="view-schedule"),
    path('lead/appointments', views.appointment, name='appointment'),
    path('estate/blog', views.estate_blog, name='estate-blog'),
    path('mylistings', views.manage_listings, name='listings'),
    path('edit_schedule/<appointment_id>', views.edit_appointment, name='edit-schedule'),
    path('lead_list/<appointment_id>', views.view_client, name='view-client'),
    path('add_client/<lead_uuid>/<appointment_id>', views.add_client, name='add-client'),
    path('del_client_info/<appointment_id>', views.delete_client, name='delete-client-info')
]
