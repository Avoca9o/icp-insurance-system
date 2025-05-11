from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session

from bot.config.db_config import Base, DATABASE_URL
from bot.models.company_info import CompanyInfo
from bot.models.insurer_scheme import InsurerScheme
from bot.models.payout import Payout
from bot.models.user_info import UserInfo
from bot.utils.logger import logger

class DBClient:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

    def get_user_by_email(self, email: str) -> UserInfo:
        try:
            user = self.Session.query(UserInfo).filter_by(email=email).first()
            logger.info(f'Database search user by email: {email}')
            return user
        except Exception as e:
            logger.error(f'Error during searching user by email {email}: {e}')
            return None
        finally:
            self.Session.remove()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> UserInfo:
        try:
            user = self.Session.query(UserInfo).filter_by(telegram_id=telegram_id).first()
            logger.info(f'Database search user by Telegram ID: {telegram_id}')
            return user
        except Exception as e:
            logger.error(f'Error during searching user by telegram_id {telegram_id}: {e}')
            return None
        finally:
            self.Session.remove()
    
    def update_user_info(self, user: UserInfo) -> bool:
        try:
            self.Session.add(user)
            self.Session.commit()
            logger.info(f'Database updating user with ID: {user.id}')
            return True
        except Exception as e:
            self.Session.rollback()
            logger.error(f'Error during updating user {user.id}: {e}')
            return False
        finally:
            self.Session.remove()
    
    def get_insurer_scheme(self, insurer_id, global_version_num) -> InsurerScheme:
        try:
            scheme = self.Session.query(InsurerScheme).filter_by(company_id=insurer_id, global_version_num=global_version_num).first()
            logger.info(f'Database search insurer scheme by global number: {global_version_num}')
            return scheme
        except Exception as e:
            logger.error(f'Error to fetch insurer scheme for company_id {insurer_id}: {e}')
            return None
        finally:
            self.Session.remove()
    
    def get_insurance_company_by_id(self, company_id):
        try:
            company = self.Session.query(CompanyInfo).filter_by(id=company_id).first()
            logger.info(f'Database search insurer by ID: {company_id}')
            return company
        except Exception as e:
            logger.error(f'Failed to fetch insurance company for company_id {company_id}: {e}')
            return None
        finally:
            self.Session.remove()
    
    def get_most_popular_insurers(self):
        try:
            top_companies = (
                self.Session.query(
                    CompanyInfo,
                    func.count(UserInfo.id).label('client_count')
                )
                .outerjoin(UserInfo)
                .group_by(CompanyInfo.id)
                .order_by(func.count(UserInfo.id).desc())
                .limit(7)
                .all()
            )
            logger.info('Database search list of the most popular insurers')
            return top_companies
        except Exception as e:
            logger.error(f'Failed to fetch most popular insurance companies: {e}')
            return []
        finally:
            self.Session.remove()
    
    def get_payout(self, user_id: int, diagnosis_code: str, diagnosis_date: datetime.date) -> Payout:
        try:
            payout = self.Session.query(Payout).filter_by(user_id=user_id, diagnosis_code=diagnosis_code, diagnosis_date=diagnosis_date).first()
            logger.info(f'Database search payout by client ID: {user_id}')
            return payout
        except Exception as e:
            logger.error(f'Error during searching payout for user {user_id}: {e}')
            return None
        finally:
            self.Session.remove()

    def add_payout(self, payout: Payout) -> bool:
        try:
            self.Session.add(payout)
            self.Session.commit()
            logger.info(f'Database add payout: {payout.id}')
            return True
        except Exception as e:
            self.Session.rollback()
            logger.error(f'Error during adding payout for user {payout.user_id}: {e}')
            return False
        finally:
            self.Session.remove()
