from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String

from config.db_config import Base

class Payout(Base):
    __tablename__ = 'payouts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), nullable=False, unique=True)
    amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    diagnosis_code = Column(String(16), nullable=False)
    diagnosis_date = Column(Date, nullable=False)

    def __init__(self, transaction_id, amount, user_id, date, company_id, diagnosis_code, diagnosis_date):
        self.transaction_id = transaction_id
        self.amount = amount
        self.user_id = user_id
        self.date = date
        self.company_id = company_id
        self.diagnosis_code = diagnosis_code
        self.diagnosis_date = diagnosis_date
