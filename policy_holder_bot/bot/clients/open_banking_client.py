import requests
import aiohttp

from bot.config.open_banking_config import OPEN_BANKING_URL
from bot.utils.logger import logger

class OpenBankingClient:
    def __init__(self):
        self.url = OPEN_BANKING_URL
    
    async def get_oauth_token(self):
        api_url = f'{self.url}/open-data/v1.0/mfsp/token'
        payload ={
            'username': 'johndoe@example.com',
            'password': 'secret',
        }
        headers = {
            'Content-Type': 'application/json',
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        api_data = await response.json()
                        return api_data
                    else:
                        return ''
            except Exception as e:
                raise Exception('Error while connecting to Open Banking API')