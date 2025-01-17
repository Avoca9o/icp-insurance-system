from config.db_config import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime


class UserInfo(Base):
    __tablename__ = 'payouts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), nullable=False, unique=True)
    amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
