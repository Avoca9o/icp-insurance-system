from datetime import datetime
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent

from config.icp_config import ICP_CANISTER_ID, ICP_CANISTER_URL, candid
from utils.logger import logger

class ICPClient:
    def __init__(self):
        identity = Identity()
        client = Client(url=ICP_CANISTER_URL)
        agent = Agent(identity, client)
        self.canister = Canister(agent=agent, canister_id=ICP_CANISTER_ID, candid=candid)

    def payout_request(
        self,
        amount: int,
        diagnosis_code: str,
        diagnosis_date: datetime.date,
        crypto_wallet: str,
        insurer_crypto_wallet: str,
    ) -> bool:
        response = self.canister.request_payout(diagnosis_code, str(diagnosis_date), insurer_crypto_wallet, crypto_wallet, int(amount))
        logger.info(response)
        if response:
            logger.info('Canister is alive')
            return True
        else:
            logger.error('Canister is not alive')
            return False
