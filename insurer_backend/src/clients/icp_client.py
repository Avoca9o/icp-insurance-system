import random

MAIN_ADDRESS = "123.234.345"


class ICPClient:
    @staticmethod
    def get_balance(company: str):
        return random.randint(0, 100000)

    @staticmethod
    def withdraw(company: str):
        # make request to icppp
        # raise exception if not success
        return None

