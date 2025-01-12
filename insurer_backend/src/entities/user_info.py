from config.db_config import Base
from sqlalchemy import Column, Integer, String, ForeignKey


class UserInfo(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(16), nullable=False, unique=True)
    insurance_amount = Column(Integer, nullable=False)
    payout_address = Column(String(64), nullable=False)
    insurer_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    schema_version = Column(Integer, ForeignKey('insurer_schemas.global_version_num'), nullable=False)
    secondary_filters = Column(String, nullable=True)
