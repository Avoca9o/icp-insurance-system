from config.db_config import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime


class Payout(Base):
    __tablename__ = 'payouts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), nullable=False, unique=True)
    amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
