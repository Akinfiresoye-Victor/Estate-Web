import uuid
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .paystack import initialize_payment, verify_payment
from .models import Subscription
import traceback
from core.models import ErrorLog
import json, hashlib, hmac
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from decouple import config
from django.contrib import messages


PLAN_PRICES = {
    "growth": 15000,
    "enterprise": 40000,
    "active_agent": 5000,
    "top_producer": 12000,
    "landlord_pro": 3000,
    "vip_hunter": 1500,
}

@login_required
def initiate_payment(request, plan):
    try:
        FREE_PLANS = ["starter", "basic", "landlord_basic", "standard"]

        if plan in FREE_PLANS:
            sub, _ = Subscription.objects.get_or_create(user=request.user)
            sub.plan = plan
            sub.is_active = True
            sub.expiry_date = None  # free plans don't expire
            sub.save()
            return render(request, 'payments/success.html')
        if plan not in PLAN_PRICES:
            return redirect("pricing_page")  # redirect to your pricing page

        amount = PLAN_PRICES[plan]
        reference = str(uuid.uuid4()).replace("-", "")[:20]  # unique payment ID
        callback_url = request.build_absolute_uri(f"/payments/verify/{reference}/{plan}/")

        result = initialize_payment(request.user.email, amount, reference, callback_url)

        if result.get("status"):
            return redirect(result["data"]["authorization_url"])  # send user to Paystack page
        
        return render(request, "payments/error.html", {"message": "Could not initiate payment"})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



@login_required
def verify_payment_view(request, reference, plan):
    try:
        result = verify_payment(reference)

        if result.get("status") and result["data"]["status"] == "success":
            sub, _ = Subscription.objects.get_or_create(user=request.user)
            sub.plan = plan
            sub.is_active = True
            sub.paystack_reference = reference
            sub.expiry_date = timezone.now() + timedelta(days=30)
            sub.save()
            return render(request, 'payments/success.html') # your success page

        return render(request, "payments/error.html", {"message": "Payment failed or not verified"})
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})



@csrf_exempt
def paystack_webhook(request):

    secret = config("PAYSTACK_SECRET_KEY").encode("utf-8")
    signature = request.headers.get("x-paystack-signature", "")
    
    body = request.body
    computed = hmac.new(secret, body, hashlib.sha512).hexdigest()

    if computed != signature:
        return HttpResponse(status=400)

    event = json.loads(body)

    if event["event"] == "charge.success":
        ref = event["data"]["reference"]
        email = event["data"]["customer"]["email"]
        pass

    return HttpResponse(status=200)




@login_required
def pricing_page(request):
    role = request.user.role
    if role == 'company':
        base_template = 'company/base.html'
    elif role == 'agent':
        base_template = 'agent/base.html'
    elif role == 'landlord':
        base_template = 'landlord/base.html'
    else:
        base_template='estate/base.html'
    role_plans = {
        "company": ["starter", "growth", "enterprise"],
        "agent": ["basic", "active_agent", "top_producer"],
        "landlord": ["landlord_basic", "landlord_pro"],
        "customer": ["standard", "vip_hunter"],
    }

    # get the current user's subscription if it exists
    try:
        current_plan = request.user.subscription.plan
    except:
        current_plan = "free"
    if current_plan== "free":
        messages.success(request, "🚀 Launch Promo: Claim your 3 months of free access today!")

    plans = role_plans.get(role, [])

    return render(request, "payments/pricing.html", {
        "plans": plans,
        "role": role,
        "current_plan": current_plan,
        'base_template': base_template
    })



def monthly_promo(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Login Required')
        return redirect('landing')
    try:
        if request.user.role=='customer':
            plan="vip_hunter"
        elif request.user.role == 'agent':
            plan='active_agent'
        
        elif request.user.role == 'company':
            plan='growth'
        
        elif request.user.role == 'landlord':
            plan='landlord_pro'
        else:
            messages.error(request, 'an error occured')
            return redirect('landing')
        sub, _ = Subscription.objects.get_or_create(user=request.user)
        sub.plan = plan
        sub.is_active = True
        sub.paystack_reference = 'Launch Month Promo'
        sub.expiry_date = timezone.now() + timedelta(days=90)
        sub.save()
        return render(request, 'payments/success.html')
    except Exception:
        error = ErrorLog.objects.create(traceback=traceback.format_exc())
        return render(request, 'estate/error_page.html', {'ref_id': error.ref_id})