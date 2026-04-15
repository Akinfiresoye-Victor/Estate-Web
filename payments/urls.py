# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("pay/<str:plan>/", views.initiate_payment, name="initiate_payment"),
    path("verify/<str:reference>/<str:plan>/", views.verify_payment_view, name="verify_payment"),
    path("payments/webhook/", views.paystack_webhook, name="paystack_webhook"),
    path("subscription/pricing", views.pricing_page, name='pricing_page'),
    path("launch/promo", views.monthly_promo, name='claim-plan')
]