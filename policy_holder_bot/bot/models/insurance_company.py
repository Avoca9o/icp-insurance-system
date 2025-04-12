from sqlalchemy import Column, Integer, String, Boolean
from bot.config.db_config import Base

class InsuranceCompany(Base):
    __tablename__ = 'insurance_companies'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    pay_address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'is_active' not in kwargs:
            self.is_active = True

    def __repr__(self):
        return f"<InsuranceCompany(id={self.id}, name='{self.name}')>" 