from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String

from bot.config.db_config import Base

class UserInfo(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(64), nullable=False, unique=True)
    telegram_id = Column(Integer, nullable=True)
    insurance_amount = Column(Integer, nullable=False)
    payout_address = Column(String(64), nullable=True)
    insurer_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    schema_version = Column(Integer, ForeignKey('insurer_schemas.global_version_num'), nullable=False)
    secondary_filters = Column(String, nullable=True)
    is_approved = Column(Boolean, nullable=False, default=False)
    sign_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)

    def __init__(self, phone, email, insurance_amount, payout_address, insurer_id, schema_version, secondary_filters):
        self.phone = phone
        self.email = email
        self.insurance_amount = insurance_amount
        self.payout_address = payout_address
        self.insurer_id = insurer_id
        self.schema_version = schema_version
        self.secondary_filters = secondary_filters
        self.is_approved = False
