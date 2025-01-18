from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from bot.config import Base


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


class UserInfo(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(16), nullable=False, unique=True)
    insurance_amount = Column(Integer, nullable=False)
    insurer_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    schema_version = Column(Integer, ForeignKey('insurer_schemas.global_version_num'), nullable=False)
    secondary_filters = Column(String, nullable=True)
    telegram_id = Column(Integer, nullable=True)
    is_approved = Column(Boolean, nullable=False)

    def __init__(self, phone, insurance_amount, insurer_id, schema_version, secondary_filters):
        self.phone = phone
        self.insurance_amount = insurance_amount
        self.insurer_id = insurer_id
        self.schema_version = schema_version
        self.secondary_filters = secondary_filters
        self.is_approved = False

