import random

import asyncio
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import Types

from config.canister_did import candid

# CANISTER_ID = "be2us-64aaa-aaaaa-qaabq-cai"
CANISTER_ID = "bkyz2-fmaaa-aaaaa-qaaaq-cai"

iden = Identity()
client = Client(url="http://127.0.0.1:4943")
agent = Agent(iden, client)

canister = Canister(agent=agent, canister_id=CANISTER_ID, candid=candid)


class ICPClient:
    @staticmethod
    def get_balance(company_pay_address: str):
        res = canister.get_insurer_balance(company_pay_address)

        return res[0]['ok']

    @staticmethod
    def withdraw(company: str):
        # make request to icppp
        # raise exception if not success
        return None

    @staticmethod
    def check_canister_health():
        res = canister.get_insurance_case_info()
        if res:
            print("Canister is alive")
        else:
            print("Canister is not alive")

    @staticmethod
    def register_company(payout_address: str):
        print('trying to register company in canister')
        canister.register_insurer(payout_address)
        print('company is registered in canister')

        return None

