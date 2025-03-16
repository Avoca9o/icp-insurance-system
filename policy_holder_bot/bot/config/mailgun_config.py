import os
from dotenv import load_dotenv

load_dotenv()

MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
