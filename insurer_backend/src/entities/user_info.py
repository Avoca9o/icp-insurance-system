from config.db_config import Base
from sqlalchemy import Column, Integer, String


class UserInfo(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(16), nullable=False)
    payout_address = Column(String(64), nullable=False)
    insurer = Column(String(64), nullable=False)
    schema = Column(Integer, nullable=False)
    secondary_filters = Column(String(512), nullable=True)
