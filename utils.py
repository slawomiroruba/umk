# utils.py
import logging
import os
from email.mime.text import MIMEText
import smtplib
import traceback
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_RECIPIENT

def setup_logging():
    log_file_path = os.path.join(os.path.dirname(__file__), 'update_subscriptions.log')
    logging.basicConfig(
        filename=log_file_path,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def send_error_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USERNAME
    msg['To'] = EMAIL_RECIPIENT

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, [EMAIL_RECIPIENT], msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(f"Error sending email: {traceback.format_exc()}")
