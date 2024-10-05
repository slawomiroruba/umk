# getresponse_api.py
import requests
from config import GETRESPONSE_API_KEY, GETRESPONSE_API_URL
import logging
import time

headers = {
    "X-Auth-Token": f"api-key {GETRESPONSE_API_KEY}",
    "Content-Type": "application/json"
}

def get_contact_custom_field_value(contact_id, custom_field_id):
    """
    Pobiera wartość niestandardowego pola dla kontaktu z GetResponse.
    
    :param contact_id: ID kontaktu w GetResponse.
    :param custom_field_id: ID niestandardowego pola (custom field).
    :return: Wartość pola niestandardowego lub None, jeśli pole nie istnieje.
    """
    try:
        # Pobierz szczegóły kontaktu z GetResponse
        response = requests.get(f"{GETRESPONSE_API_URL}/contacts/{contact_id}", headers=headers)
        
        if response.status_code == 200:
            contact_details = response.json()

            # Sprawdź, czy kontakt ma przypisane niestandardowe pola
            if 'customFieldValues' in contact_details:
                for field in contact_details['customFieldValues']:
                    if field['customFieldId'] == custom_field_id:
                        # Zwróć wartość pola (zakładam, że pole może mieć jedną wartość)
                        return field['value'][0] if field['value'] else None
            return None
        else:
            logging.error(f"Error retrieving contact {contact_id}: status_code = {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Failed to get custom field value for contact {contact_id}: {e}")
        return None


def get_campaign_id(campaign_name):
    """Get the campaign ID for a given campaign name."""
    params = {"query[name]": campaign_name}
    response = requests.get(f"{GETRESPONSE_API_URL}/campaigns", headers=headers, params=params)
    campaigns = response.json()
    if campaigns:
        return campaigns[0]['campaignId']
    else:
        logging.error(f"Campaign '{campaign_name}' not found in GetResponse.")
        return None

def get_all_contacts_from_campaign(campaign_id):
    """Retrieve all contacts from a specific campaign."""
    contacts = []
    page = 1
    per_page = 1000  # Adjust per_page according to GetResponse limits

    while True:
        params = {
            "query[campaignId]": campaign_id,
            "page": page,
            "perPage": per_page
        }
        response = requests.get(f"{GETRESPONSE_API_URL}/contacts", headers=headers, params=params)
        data = response.json()
        if not data:
            break
        contacts.extend(data)
        page += 1

    return contacts

def build_email_contact_map(contacts):
    """Create a map of email to contact ID."""
    email_contact_map = {}
    for contact in contacts:
        email = contact['email'].lower()
        contact_id = contact['contactId']
        email_contact_map[email] = contact_id
    return email_contact_map

def get_contact_by_email(email):
    params = {
        "query[email]": email
    }
    response = requests.get(f"{GETRESPONSE_API_URL}/contacts", headers=headers, params=params)
    if response.status_code == 200:
        contacts = response.json()
        if contacts:
            return contacts[0]
        else:
            return None
    else:
        logging.error(f"Error retrieving contact {email}: status_code = {response.status_code}, Response: {response.text}")
        return None

def search_contact_by_email(email):
    data = {
        "query": {
            "email": email
        },
        "additionalFlags": ["includeUnconfirmed"]
    }
    response = requests.post(f"{GETRESPONSE_API_URL}/search-contacts", headers=headers, json=data)
    if response.status_code == 200:
        contacts = response.json()
        if contacts:
            return contacts[0]
        else:
            return None
    else:
        logging.error(f"Błąd podczas wyszukiwania kontaktu {email}: status_code = {response.status_code}, Response: {response.text}")
        return None



def get_custom_field_id(field_name):
    """Get the custom field ID for a given field name."""
    params = {"query[name]": field_name}
    response = requests.get(f"{GETRESPONSE_API_URL}/custom-fields", headers=headers, params=params)
    fields = response.json()
    if fields:
        return fields[0]['customFieldId']
    else:
        logging.error(f"Custom field '{field_name}' not found in GetResponse.")
        return None

def update_contact_custom_field(contact_id, email, field_id, value):
    """Update a custom field for a contact."""
    data = {
        "customFieldValues": [
            {
                "customFieldId": field_id,
                "value": [value]
            }
        ]
    }
    response = requests.post(f"{GETRESPONSE_API_URL}/contacts/{contact_id}", headers=headers, json=data)
    if response.status_code != 200:
        logging.error(f"Error updating {email}: status_code = {response.status_code}, Response: {response.text}")

def create_contact_in_getresponse(email, name, campaign_id):
    data = {
        "email": email,
        "name": name,
        "campaign": {
            "campaignId": campaign_id
        }
    }
    response = requests.post(f"{GETRESPONSE_API_URL}/contacts", headers=headers, json=data)
    logging.info(f"Create contact response status: {response.status_code}")
    logging.info(f"Create contact response content: {response.text}")
    
    if response.status_code in [200, 201, 202]:
        print(f"Utworzono nowy kontakt: {email}")
        # Mechanizm ponawiania
        max_retries = 5
        delay = 2  # sekundy
        for attempt in range(max_retries):
            time.sleep(delay)
            contact = get_contact_by_email(email)
            if contact:
                return contact
            else:
                logging.info(f"Próba {attempt + 1} pobrania kontaktu {email} nieudana.")
            delay *= 2  # Zwiększ opóźnienie
        logging.error(f"Nie udało się pobrać kontaktu {email} po utworzeniu po {max_retries} próbach.")
        return None
    else:
        logging.error(f"Błąd podczas tworzenia kontaktu {email}: status_code = {response.status_code}, Response: {response.text}")
        return None
