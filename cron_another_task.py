# cron_another_task.py
from woocommerce_api import get_wcapi
from getresponse_api import some_other_function
from utils import send_error_email, setup_logging
import logging

def main():
    try:
        setup_logging()
        wcapi = get_wcapi()
        # Your code here
    except Exception as e:
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        logging.error(f"An error occurred: {error_message}")
        subject = "Error in cron_another_task.py"
        body = f"An error occurred during the execution of the script:\n\n{error_message}"
        send_error_email(subject, body)

if __name__ == "__main__":
    main()
