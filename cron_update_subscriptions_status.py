# cron_update_subscriptions_status.py
import traceback
import concurrent.futures
from woocommerce_api import get_wcapi, get_all_subscriptions
from getresponse_api import (
    get_campaign_id, get_all_contacts_from_campaign,
    build_email_contact_map, get_custom_field_id,
    update_contact_custom_field, create_contact_in_getresponse
)
from utils import send_error_email, setup_logging
import logging

def extract_subscription_data(subscriptions):
    """Extract email, status, and name from subscriptions."""
    subscription_data = {}
    subscription_names = {}
    for sub in subscriptions:
        email = sub['billing']['email']
        status = sub['status']
        first_name = sub['billing']['first_name']
        last_name = sub['billing']['last_name']
        name = f"{first_name} {last_name}".strip()
        subscription_data[email] = status
        subscription_names[email] = name
    return subscription_data, subscription_names

def update_contacts_in_parallel(updates):
    """Update contacts in parallel using threading."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_contact_custom_field, *update) for update in updates]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error updating contact: {traceback.format_exc()}")

def main():
    try:
        setup_logging()
        wcapi = get_wcapi()

        custom_field_id = get_custom_field_id('active_subscription')
        if not custom_field_id:
            print("Custom field 'active_subscription' does not exist in GetResponse.")
            return

        subscriptions = get_all_subscriptions(wcapi)
        subscription_data, subscription_names = extract_subscription_data(subscriptions)

        campaign_id = get_campaign_id('Jacek Walkiewicz')
        if not campaign_id:
            print("Campaign 'Jacek Walkiewicz' does not exist in GetResponse.")
            return

        contacts = get_all_contacts_from_campaign(campaign_id)
        email_contact_map = build_email_contact_map(contacts)

        updates = []
        for email, status in subscription_data.items():
            email_lower = email.lower()
            active_value = '1' if status == 'active' else '0'
            if email_lower in email_contact_map:
                contact_id = email_contact_map[email_lower]
                updates.append((contact_id, email, custom_field_id, active_value))
            else:
                print(f"Contact {email} not found in GetResponse.")
                # name = subscription_names.get(email, '')
                # new_contact = create_contact_in_getresponse(email, name, campaign_id)
                # if new_contact:
                #     contact_id = new_contact['contactId']
                #     updates.append((contact_id, email, custom_field_id, active_value))
                # else:
                #     logging.error(f"Failed to create or retrieve contact ID for {email}.")

        if updates:
            update_contacts_in_parallel(updates)

    except Exception as e:
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        logging.error(f"An error occurred: {error_message}")
        subject = "Error in cron_update_subscriptions_status.py"
        body = f"An error occurred during the execution of the script:\n\n{error_message}"
        send_error_email(subject, body)

if __name__ == "__main__":
    main()
