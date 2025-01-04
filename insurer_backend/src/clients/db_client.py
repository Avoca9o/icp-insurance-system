from typing import Dict
from entities.company_info import CompanyInfo
from entities.user_info import UserInfo

from config.db_config import Base, SessionLocal


class DBClient:
    @staticmethod
    def add_company(company: CompanyInfo):
        session = SessionLocal()

        if session.query(CompanyInfo).filter(CompanyInfo.login == company.login).first():
            raise ValueError("company with login {} already exists".format(company.login))

        session.add(company)
        session.commit()
        session.close()

    @staticmethod
    def authorize_company(login: str, password: str):
        session = SessionLocal()

        company = session.query(CompanyInfo).filter(CompanyInfo.login == login).first()
        if company is None:
            raise ValueError("No such login exists")

        if company.password != password:
            raise ValueError("Invalid password")

        session.commit()
        session.close()

    @staticmethod
    def add_user(user: UserInfo):
        session = SessionLocal()

        if session.query(UserInfo).filter(UserInfo.phone == user.phone).first():
            raise ValueError("user with phone number {} already exists".format(user.phone))

        session.add(user)
        session.commit()
        session.close()

    @staticmethod
    def update_user(user: UserInfo):
        session = SessionLocal()

        db_user = session.query(UserInfo).filter(UserInfo.phone == user.phone).first()

        if db_user is None:
            raise ValueError("user with phone number {} not exists".format(user.phone))

        if user.payout_address is not None:
            db_user.payout_address = user.payout_address

        if user.schema is not None:
            db_user.schema = user.schema

        if user.secondary_filters is not None:
            db_user.secondary_filters = user.secondary_filters

        session.commit()
        session.close()
