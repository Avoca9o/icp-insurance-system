from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String

from config import Base


class CompanyInfo(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(64), nullable=False, unique=True)
    name = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    pay_address = Column(String(64), nullable=False)

    def __init__(self, login, password, name, email, pay_address):
        self.login = login
        self.password = password
        self.name = name
        self.email = email
        self.pay_address = pay_address


class InsurerScheme(Base):
    __tablename__ = 'insurer_schemas'

    global_version_num = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    diagnoses_coefs = Column(String, nullable=False)

    def __init__(self, company_id, diagnoses_coefs):
        self.company_id = company_id
        self.diagnoses_coefs = diagnoses_coefs


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

    def __init__(self, phone, email, insurance_amount, payout_address, insurer_id, schema_version, secondary_filters):
        self.phone = phone
        self.email = email
        self.insurance_amount = insurance_amount
        self.payout_address = payout_address
        self.insurer_id = insurer_id
        self.schema_version = schema_version
        self.secondary_filters = secondary_filters
        self.is_approved = False

