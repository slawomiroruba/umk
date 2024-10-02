import os
import smtplib
from email.mime.text import MIMEText
import traceback
import requests
from woocommerce import API
import concurrent.futures

# Konfiguracja SMTP
smtp_server = "smtp.zenbox.pl"
smtp_port = 587
smtp_username = os.environ.get('SMTP_USERNAME')
smtp_password = os.environ.get('SMTP_PASSWORD')
email_recipient = "slawomir.oruba@gmail.com"  # Wpisz adres e-mail odbiorcy

def send_error_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_username
    msg['To'] = email_recipient

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, [email_recipient], msg.as_string())
        server.quit()
        print("Wysłano e-mail z informacją o błędzie.")
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")

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

def get_campaign_id(campaign_name):
    params = {
        "query[name]": campaign_name
    }
    response = requests.get(f"{getresponse_api_url}/campaigns", headers=headers, params=params)
    campaigns = response.json()
    if campaigns:
        return campaigns[0]['campaignId']
    else:
        return None

def get_all_contacts_from_campaign(campaign_id):
    contacts = []
    page = 1
    per_page = 1000

    while True:
        params = {
            "query[campaignId]": campaign_id,
            "page": page,
            "perPage": per_page
        }
        response = requests.get(f"{getresponse_api_url}/contacts", headers=headers, params=params)
        data = response.json()
        if not data:
            break
        contacts.extend(data)
        page += 1

    return contacts

def build_email_contact_map(contacts):
    email_contact_map = {}
    for contact in contacts:
        email = contact['email'].lower()
        contact_id = contact['contactId']
        email_contact_map[email] = contact_id
    return email_contact_map

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

def update_contact_custom_field(contact_id, email, field_id, value):
    data = {
        "customFieldValues": [
            {
                "customFieldId": field_id,
                "value": [value]
            }
        ]
    }
    response = requests.post(f"{getresponse_api_url}/contacts/{contact_id}", headers=headers, json=data)
    if response.status_code == 200:
        print(f"Zaktualizowano {email}: active_subscription = {value}")
    else:
        print(f"Błąd podczas aktualizacji {email}: status_code = {response.status_code}, Response: {response.text}")

def update_contacts_in_parallel(updates):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_contact_custom_field, *update) for update in updates]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Wystąpił błąd: {e}")

def main():
    try:
        custom_field_id = get_custom_field_id('active_subscription')
        if not custom_field_id:
            print("Pole 'active_subscription' nie istnieje w GetResponse.")
            return

        # Pobierz wszystkie subskrypcje z WooCommerce
        subscriptions = get_all_subscriptions()
        subscription_data = extract_subscription_data(subscriptions)

        # Pobierz ID kampanii (listy) 'Jacek Walkiewicz'
        campaign_id = get_campaign_id('Jacek Walkiewicz')
        if not campaign_id:
            print("Kampania 'Jacek Walkiewicz' nie istnieje w GetResponse.")
            return

        # Pobierz wszystkie kontakty z kampanii
        contacts = get_all_contacts_from_campaign(campaign_id)
        email_contact_map = build_email_contact_map(contacts)

        # Przygotuj listę aktualizacji
        updates = []
        for email, status in subscription_data.items():
            email_lower = email.lower()
            if email_lower in email_contact_map:
                contact_id = email_contact_map[email_lower]
                active_value = '1' if status == 'active' else '0'
                updates.append((contact_id, email, custom_field_id, active_value))
            else:
                print(f"Kontakt {email} nie znaleziony w GetResponse.")

        # Wykonaj aktualizacje równolegle
        update_contacts_in_parallel(updates)

    except Exception as e:
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        subject = "Błąd w skrypcie update_subscriptions.py"
        body = f"Wystąpił błąd podczas wykonywania skryptu:\n\n{error_message}"
        send_error_email(subject, body)
        print("Wystąpił błąd. Wysłano e-mail z informacją o błędzie.")

if __name__ == "__main__":
    main()