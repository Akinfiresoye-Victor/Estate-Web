from django.urls import path
from core import views as core_views
from core import ai_features as ai

urlpatterns = [
    path('waitlist-signup/', core_views.waitlist_signup, name='waitlist-signup'),

    path('', core_views.landing_page, name='landing'),
    path('about/', core_views.about_page, name='about'),
    path('feedback/', core_views.feedbacks, name='feedback'),
    path('feedback/submit/', core_views.submit_feedback, name='submit_feedback'),
    path('delete_property_r/<property_id>/', core_views.delete_property_on_lease, name="delete-property-r"),
    path('delete_property_s/<property_id>/', core_views.delete_property_on_sale, name="delete-property-s"),
    path('update_property/<property_id>/', core_views.update_property_rent, name="update-property"),
    path('update_property_s/<property_id>/', core_views.update_property_sale, name="update-property-s"),
    path('sell_property/', core_views.sell_property, name="sell-property"),
    path('lease_property/', core_views.lease_property, name="lease-property"),
    path('latest_news/', core_views.articles, name='articles'),
    path('estateweb/partners/', core_views.partner_with_us, name="partner-with-us"),
    path('add_schedule', core_views.add_schedule, name="add-schedule"),
    path('schedule_detail/<appt_uuid>', core_views.appointment_detail, name="view-schedule"),
    path('appointments/', core_views.appointment, name='appointment'),
    path('estate/blog', core_views.estate_blog, name='estate-blog'),
    path('mylistings', core_views.manage_listings, name='listings'),
    path('edit_schedule/<appointment_uuid>', core_views.edit_appointment, name='edit-schedule'),
    path('lead_list/<appointment_uuid>', core_views.view_client, name='view-client'),
    path('add_client/<lead_uuid>/<appointment_uuid>', core_views.add_client, name='add-client'),
    path('del_client_info/<appointment_uuid>', core_views.delete_client, name='delete-client-info'),
    path('terms/privacy_terms', core_views.privacy_terms_sheet, name='terms-agreement'),
    path('terms/partnership_terms', core_views.partnership_terms, name='partnership-terms'),
    path('patner_form_filled', core_views.partner_success, name='partner-success'),
    path('schedule/delete/<appointment_uuid>', core_views.delete_appointment, name='delete-appointment'),
    path('faq', core_views.estate_web_guide, name='faq'),
    path('toggle_listing/<str:property_type>/<int:property_id>/', core_views.toggle_listing, name='toggle-listing'),
    path('ai-description/', ai.ai_description_generator, name='ai-description'),
    path('ai-summarize-lead/<int:lead_id>/', ai.ai_lead_summarize, name='ai-lead-summarize'),
    path('report_user/<int:reportee_id>/<str:reportee_role>', core_views.report_user, name='report-user')
    
]

