from typing import Dict
from entities.company_info import CompanyInfo
from entities.user_info import UserInfo


class DBClient:
    companies: Dict[str, CompanyInfo] = {}
    users: Dict[str, UserInfo] = {}

    @staticmethod
    def add_company(company: CompanyInfo):
        if company.login in DBClient.companies:
            raise ValueError("company with login {} already exists".format(company.login))

        DBClient.companies[company.login] = company

    @staticmethod
    def authorize_company(login: str, password: str):
        if login not in DBClient.companies:
            raise ValueError("No such login exists")

        if password != DBClient.companies[login].password:
            raise ValueError("Invalid password")

    @staticmethod
    def add_user(user: UserInfo):
        if user.phone in DBClient.users:
            raise ValueError("user with phone number {} already exists".format(user.phone))

        DBClient.users[user.phone] = user

    @staticmethod
    def update_user(user: UserInfo):
        if user.phone not in DBClient.users:
            raise ValueError("user with phone number {} not exists".format(user.phone))

        if user.payout_address is not None:
            DBClient.users[user.phone].payout_address = user.payout_address

        if user.schema is not None:
            DBClient.users[user.phone].schema = user.schema

        if user.secondary_filters is not None:
            DBClient.users[user.phone].secondary_filters = user.secondary_filters
