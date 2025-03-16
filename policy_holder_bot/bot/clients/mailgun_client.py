import requests
from config.mailgun_config import MAILGUN_API_KEY, MAILGUN_DOMAIN, SENDER_EMAIL
from utils.logger import logger

class MailgunClient:
    def __init__(self):
        self.mailgun_api_key = MAILGUN_API_KEY
        self.mailgun_domain = MAILGUN_DOMAIN
        self.sender_email = SENDER_EMAIL
    
    def send_email(self, to, subject, text):
        response = requests.post(
            f'https://api.mailgun.net/v3/{self.mailgun_domain}/messages',
            auth=('api', self.mailgun_api_key),
            data={'from': f'Telegram bot <{self.sender_email}>',
                  'to': [to],
                  'subject': subject,
                  'text': text})
        
        if response.status_code != 200:
            logger.error(f'Error while sending verification code to {to}: {response.text}')
        
        return response.status_code == 200
