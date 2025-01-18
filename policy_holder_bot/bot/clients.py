from typing import Dict

from bot.config import canister, SessionLocal

from bot.models import CompanyInfo, InsurerScheme, UserInfo

class DBClient:
    @staticmethod
    def update_user(user: UserInfo):
        session = SessionLocal()
        db_user = session.query(UserInfo).filter(UserInfo.phone == user.phone).first()
        if db_user is None:
            raise ValueError(f'User with phone number {user.phone} does not exist')
        db_user.is_approved = True
        db_user.telegram_id = user.telegram_id

        session.commit()
        session.close()


class ICPClient:
    @staticmethod
    def get_balance(company: str):
        return 0
    
    @staticmethod
    def withdraw(company: str):
        return None
    
    @staticmethod
    def check_canister_health():
        response = canister.get_insurance_case_info()
        if response:
            print('Canister is alive')
        else:
            print('Canister is not alive')