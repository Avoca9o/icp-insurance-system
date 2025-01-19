import random

import asyncio
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import Types

from config.canister_did import candid

iden = Identity()
client = Client(url="http://127.0.0.1:4943")
agent = Agent(iden, client)

canister = Canister(agent=agent, canister_id="bkyz2-fmaaa-aaaaa-qaaaq-cai", candid=candid)


class ICPClient:
    @staticmethod
    def get_balance(company: str):
        return random.randint(0, 100000)

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
        # todo: воспользоваться нормально и обработать после того как станет доступно
        # res = canister.register(payout_address)

        return None

