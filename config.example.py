import os

# Klucze API WooCommerce
wc_url = "https://umk.jacekwalkiewicz.pl"
wc_consumer_key = "ck_2cfea7eb297c277c03b50eef2ead4d1a80b035d4"
wc_consumer_secret = "cs_2f73a819912b1207c5b795f2b5eff1521baaa33b"

# Klucz API GetResponse
getresponse_api_key = "p250s10qs04dajmqiiha0690jolgxfs0"

# Konfiguracja SMTP
smtp_server = "smtp.zenbox.pl"
smtp_port = 587
smtp_username = os.environ.get('SMTP_USERNAME')
smtp_password = os.environ.get('SMTP_PASSWORD')
email_recipient = "slawomir.oruba@gmail.com"  # Wpisz adres e-mail odbiorcy
