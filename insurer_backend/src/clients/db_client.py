from typing import Dict

from sqlalchemy import and_, cast, Date

from entities.company_info import CompanyInfo
from entities.user_info import UserInfo
from entities.insurer_scheme import InsurerScheme
from entities.payout import Payout

from config.db_config import Base, SessionLocal
from utils.logger import logger


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
    def get_company(comp_id: int) -> CompanyInfo:
        session = SessionLocal()

        company = session.query(CompanyInfo).filter(CompanyInfo.id == comp_id).first()
        return company

    @staticmethod
    def authorize_company(login: str, password: str):
        session = SessionLocal()

        company = session.query(CompanyInfo).filter(CompanyInfo.login == login).first()
        if company is None:
            raise ValueError("No such login exists")

        if company.password != password:
            raise ValueError("Invalid password")

        company_id = company.id

        session.commit()
        session.close()

        return company_id

    @staticmethod
    def add_user(user: UserInfo):
        session = SessionLocal()

        if session.query(UserInfo).filter(UserInfo.email == user.email).first():
            raise ValueError("user with phone number {} already exists".format(user.email))

        session.add(user)
        session.commit()
        session.close()

    @staticmethod
    def update_user(user: UserInfo, company_id: int):
        session = SessionLocal()

        db_user = session.query(UserInfo).filter(UserInfo.email == user.email).first()

        if db_user is None:
            raise ValueError("user with email {} not exists".format(user.email))

        if db_user.insurer_id != company_id:
            raise ValueError("user with email {} is not in company's users list".format(user.email))

        if db_user.is_approved:
            raise ValueError("user with email {} has already approved his info, can't change info".format(user.email))

        logger.info(f'{user.email}, {user.insurance_amount}')

        if user.insurance_amount is not None:
            db_user.insurance_amount = user.insurance_amount

        if user.schema_version is not None:
            db_user.schema_version = user.schema_version

        if user.secondary_filters is not None:
            db_user.secondary_filters = user.secondary_filters

        session.add(db_user)
        session.commit()
        session.close()

    @staticmethod
    def add_scheme(scheme: InsurerScheme):
        logger.info(f'scheme.diagnoses_coefs')
        session = SessionLocal()

        session.add(scheme)
        session.commit()
        session.close()
    
    @staticmethod
    def get_company_name(company_id: int):
        session = SessionLocal()

        res = session.query(CompanyInfo).filter(CompanyInfo.id == company_id).first()
        session.close()

        return res.name

    @staticmethod
    def get_schemas(company_id: int):
        session = SessionLocal()

        res = session.query(InsurerScheme).filter(InsurerScheme.company_id == company_id).all()
        session.close()

        res = {'schemas': [{'id': x.global_version_num} for x in res]}
        logger.info(f'{res}')

        return res

    @staticmethod
    def get_schema(global_scheme_version: int):
        session = SessionLocal()

        res = session.query(InsurerScheme).filter(InsurerScheme.global_version_num == global_scheme_version).first()
        session.close()

        return res

    @staticmethod
    def get_users(company_id: int):
        session = SessionLocal()

        res = session.query(UserInfo).filter(UserInfo.insurer_id == company_id).all()
        session.close()

        res = {'users': [{'email': x.email} for x in res]}
        return res

    @staticmethod
    def get_user(email: str, company_id: int):
        session = SessionLocal()

        res = session.query(UserInfo).filter(UserInfo.email == email).first()
        session.close()

        if res.insurer_id != company_id:
            raise ValueError('User is not for this company')

        return {'email': res.email,
                'scheme_version': res.schema_version,
                'insurance_amount': res.insurance_amount,
                'secondary_filters': res.secondary_filters,
                'telegram_id': res.telegram_id,
                'is_approved': res.is_approved
                }


    @staticmethod
    def delete_user(email: str, company_id: int):
        session = SessionLocal()

        res = session.query(UserInfo).filter(UserInfo.email == email).first()

        if res.insurer_id != company_id:
            raise ValueError('User is not for this company')
        session.delete(res)
        session.commit()
        session.close()

    @staticmethod
    def get_payouts_by_company_and_date(company_id, target_date):
        session = SessionLocal()

        payouts = session.query(Payout).filter(
            and_(
                Payout.company_id == company_id,
                cast(Payout.date, Date) == target_date
            )
        ).all()

        session.close()
        logger.debug(f'>>>> {[{"user": payout.user_id, "amount": payout.amount, "date": str(payout.date), "diagnoses": payout.diagnosis_code} for payout in payouts]}')
        return [{'user': payout.user_id, 'amount': payout.amount, 'date': str(payout.date), 'diagnoses': payout.diagnosis_code} for payout in payouts]
