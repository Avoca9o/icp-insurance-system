from datetime import datetime
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent

from bot.config.icp_config import ICP_CANISTER_ID, ICP_CANISTER_URL, candid

class ICPClient:
    def __init__(self):
        identity = Identity()
        client = Client(url=ICP_CANISTER_URL)
        agent = Agent(identity, client)
        self.canister = Canister(agent=agent, canister_id=ICP_CANISTER_ID, candid=candid)

    def add_approved_client(
        self,
        insurer_wallet_address: str,
        policy_holder_id: int,
        checksum: str,
    ) -> bool:
        response = self.canister.add_approved_client(insurer_wallet_address, policy_holder_id, checksum)
        if response:
            return True
        else:
            return False

    def payout_request(
        self,
        amount: int,
        policy_number: str,
        diagnosis_code: str,
        diagnosis_date: datetime.date,
        crypto_wallet: str,
        insurer_crypto_wallet: str,
        oauth_token: str,
    ) -> bool:
        response = self.canister.request_payout(policy_number, diagnosis_code, str(diagnosis_date), insurer_crypto_wallet, crypto_wallet, int(amount), oauth_token)
        if 'Payout successful' in str(response):
            return True
        else:
            return False
