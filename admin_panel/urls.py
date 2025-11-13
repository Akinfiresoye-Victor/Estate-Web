from django.urls import path
from . import views



urlpatterns = [
    path('', views.admin_dashboard, name='executive'),
    path('feedbacks', views.view_feedbacks, name='view-feedbacks'),
    path('delete/<feedback_id>', views.delete_feedback, name='delete-feedback'),
    path('listed_prop/', views.all_properties, name='all-listings')
]
