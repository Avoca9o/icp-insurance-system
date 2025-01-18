from typing import Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Base, DATABASE_URL
from models import CompanyInfo, InsurerScheme, UserInfo
from utils import logger

class DBClient:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_user_by_email(self, email: str) -> UserInfo:
        session = self.Session()
        try:
            user = session.query(UserInfo).filter_by(email=email).first()
            return user
        except Exception as e:
            logger.error(f'Error during searching user by email: {e}')
        finally:
            session.close()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> UserInfo:
        session = self.Session()
        try:
            user = session.query(UserInfo).filter_by(telegram_id=telegram_id).first()
            return user
        except Exception as e:
            logger.error(f'Error during searching user by telegram_id: {e}')
        finally:
            session.close()
    
    def update_user_info(self, user: UserInfo) -> bool:
        session = self.Session()
        try:
            session.add(user)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f'Error during updating uses: {e}')
            return False
        finally:
            session.close()
    
    def get_insurer_scheme(self, insurer_id, global_version_num) -> InsurerScheme:
        session = self.Session()
        try:
            scheme = session.query(InsurerScheme).filter_by(company_id=insurer_id, global_version_num=global_version_num).first()
            return scheme
        except Exception as e:
            logger.error(f'Error to fetch insurer scheme for company_id {insurer_id}: {e}')
        finally:
            session.close()
    
    def get_insurance_company_by_id(self, company_id):
        session = self.Session()
        try:
            company = session.query(CompanyInfo).filter_by(id=company_id).first()
            return company
        except Exception as e:
            logger.error(f'Failed to fetch insurance company for company_id {company_id}: {e}')
        finally:
            session.close()

# class ICPClient:
#     @staticmethod
#     def get_balance(company: str):
#         return 0
    
#     @staticmethod
#     def withdraw(company: str):
#         return None
    
#     @staticmethod
#     def check_canister_health():
#         response = canister.get_insurance_case_info()
#         if response:
#             print('Canister is alive')
#         else:
#             print('Canister is not alive')