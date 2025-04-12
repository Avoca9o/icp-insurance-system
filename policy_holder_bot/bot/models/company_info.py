from sqlalchemy import Column, Integer, String

from bot.config.db_config import Base

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
