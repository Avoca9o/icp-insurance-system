from datetime import datetime
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Base, DATABASE_URL, ICP_CANISTER_ID, ICP_CANISTER_URL, candid
from models import CompanyInfo, InsurerScheme, Payout, UserInfo
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
    
    def get_payout(self, user_id: int, diagnosis_code: str, diagnosis_date: datetime.date) -> Payout:
        session = self.Session()
        try:
            payout = session.query(Payout).filter_by(user_id=user_id, diagnosis_code=diagnosis_code, diagnosis_date=diagnosis_date).first()
            return payout
        except Exception as e:
            logger.error(f'Error during searching payout: {e}')
        finally:
            session.close()

    def add_payout(self, payout: Payout) -> bool:
        session = self.Session()
        try:
            session.add(payout)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f'Error during updating uses: {e}')
            return False
        finally:
            session.close()


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