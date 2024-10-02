# woocommerce_api.py
from woocommerce import API
from config import WC_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET

def get_wcapi():
    """Initialize and return the WooCommerce API client."""
    wcapi = API(
        url=WC_URL,
        consumer_key=WC_CONSUMER_KEY,
        consumer_secret=WC_CONSUMER_SECRET,
        wp_api=True,
        version="wc/v3",
        timeout=10
    )
    return wcapi

def get_all_subscriptions(wcapi):
    """Retrieve all subscriptions from WooCommerce."""
    subscriptions = []
    page = 1

    while True:
        response = wcapi.get("subscriptions", params={"per_page": 100, "page": page}).json()
        if not response:
            break
        subscriptions.extend(response)
        page += 1

    return subscriptions
