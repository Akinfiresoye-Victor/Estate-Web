import requests
from decouple import config

PAYSTACK_SECRET = config('PAYSTACK_SECRET_KEY')
BASE_URL = "https://api.paystack.co"

HEADERS = {
    "Authorization": f"Bearer {PAYSTACK_SECRET}",
    "Content-Type": "application/json",
}

def initialize_payment(email, amount_naira, reference, callback_url):
    """
    Starts a payment session with Paystack.
    amount must be in KOBO (naira x 100).
    Returns the URL to redirect the user to for payment.
    """
    payload = {
        "email": email,
        "amount": amount_naira * 100,  # convert ₦ to kobo
        "reference": reference,
        "callback_url": callback_url,
    }
    response = requests.post(f"{BASE_URL}/transaction/initialize", json=payload, headers=HEADERS)
    return response.json()


def verify_payment(reference):
    """
    After user pays, call this to confirm Paystack actually received the money.
    Always verify — never trust the frontend alone.
    """
    response = requests.get(f"{BASE_URL}/transaction/verify/{reference}", headers=HEADERS)
    return response.json()