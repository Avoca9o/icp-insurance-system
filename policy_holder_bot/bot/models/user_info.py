from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from datetime import datetime
from bot.config.db_config import Base

class UserInfo(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(64), nullable=True)
    telegram_id = Column(Integer, nullable=True)
    insurance_amount = Column(Integer, nullable=True)
    payout_address = Column(String(64), nullable=True)
    insurer_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    schema_version = Column(Integer, ForeignKey('insurer_schemas.global_version_num'), nullable=True)
    secondary_filters = Column(String, nullable=True)
    is_approved = Column(Boolean, nullable=False, default=False)
    sign_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'is_approved' not in kwargs:
            self.is_approved = False
