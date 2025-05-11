import random

import asyncio
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import Types

from config.canister_did import candid
from utils.logger import logger

CANISTER_ID = "be2us-64aaa-aaaaa-qaabq-cai"
# diman
#CANISTER_ID = "bkyz2-fmaaa-aaaaa-qaaaq-cai"

iden = Identity()
client = Client(url="http://127.0.0.1:4943")
agent = Agent(iden, client)

canister = Canister(agent=agent, canister_id=CANISTER_ID, candid=candid)


class ICPClient:
    @staticmethod
    def get_balance(company_pay_address: str):
        res = canister.get_insurer_balance(company_pay_address)

        logger.info(res)

        return res[0]['ok']

    @staticmethod
    def withdraw(payout_address: str):
        res = canister.withdraw(payout_address)
        if "Err" in res:
            raise Exception(res["Err"])
        return None

    @staticmethod
    def check_canister_health():
        res = canister.get_insurance_case_info()
        if res:
            logger.info("Canister is alive")
        else:
            logger.error("Canister is not alive")

    @staticmethod
    def register_company(payout_address: str):
        logger.info('trying to register company in canister')
        canister.register_insurer(payout_address)
        logger.info('company is registered in canister')

        return None

    @staticmethod
    def is_checksum_valid(company_id, user_tg_id, current_sum):
        # res = canister.check_sum(company_id, user_tg_id, current_sum)
        # logger.debug(f'>>> {res}')
        return random.choice([True, False])
