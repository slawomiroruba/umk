from woocommerce import API
import requests


wcapi = API(
    url="https://umk.jacekwalkiewicz.pl",  # Adres URL sklepu
    consumer_key="ck_2cfea7eb297c277c03b50eef2ead4d1a80b035d4",  # Klucz API WooCommerce
    consumer_secret="cs_2f73a819912b1207c5b795f2b5eff1521baaa33b",  # Sekret API WooCommerce
    wp_api=True,
    version="wc/v3",
    timeout=10
)

getresponse_api_key = "p250s10qs04dajmqiiha0690jolgxfs0"
getresponse_api_url = "https://api.getresponse.com/v3"
headers = {
    "X-Auth-Token": f"api-key {getresponse_api_key}",
    "Content-Type": "application/json"
}

def get_all_subscriptions():
    subscriptions = []
    page = 1

    while True:
        response = wcapi.get("subscriptions", params={"per_page": 100, "page": page}).json()
        if not response:
            break
        subscriptions.extend(response)
        page += 1

    return subscriptions

def extract_subscription_data(subscriptions):
    subscription_data = {}
    for sub in subscriptions:
        email = sub['billing']['email']
        status = sub['status']
        subscription_data[email] = status
    return subscription_data

def get_contact_by_email(email):
    params = {
        "query[email]": email
    }
    response = requests.get(f"{getresponse_api_url}/contacts", headers=headers, params=params)
    contacts = response.json()
    return contacts[0] if contacts else None

def update_contact_custom_field(contact_id, email, field_id, value):
    data = {
        "email": email,
        "customFieldValues": [
            {
                "customFieldId": field_id,
                "value": [value]
            }
        ]
    }
    response = requests.post(f"{getresponse_api_url}/contacts/{contact_id}", headers=headers, json=data)
    print(f"Response status: {response.status_code}, Response text: {response.text}")
    return response.status_code

def get_custom_field_id(field_name):
    params = {
        "query[name]": field_name
    }
    response = requests.get(f"{getresponse_api_url}/custom-fields", headers=headers, params=params)
    fields = response.json()
    if fields:
        return fields[0]['customFieldId']
    else:
        return None


def main():
    custom_field_id = get_custom_field_id('active_subscription')
    if not custom_field_id:
        print("Pole 'active_subscription' nie istnieje w GetResponse.")
        return

    subscriptions = get_all_subscriptions()
    subscription_data = extract_subscription_data(subscriptions)

    for email, status in subscription_data.items():
        contact = get_contact_by_email(email)
        if contact:
            contact_id = contact['contactId']
            active_value = '1' if status == 'active' else '0'
            status_code = update_contact_custom_field(contact_id, email, custom_field_id, active_value)
            if status_code == 200:
                print(f"Zaktualizowano {email}: active_subscription = {active_value}")
            else:
                print(f"Błąd podczas aktualizacji {email}: status_code = {status_code}")
        else:
            print(f"Kontakt {email} nie znaleziony w GetResponse.")


if __name__ == "__main__":
    main()
