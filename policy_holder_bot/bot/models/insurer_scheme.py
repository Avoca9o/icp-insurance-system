from sqlalchemy import Column, ForeignKey, Integer, String

from bot.config.db_config import Base

class InsurerScheme(Base):
    __tablename__ = 'insurer_schemas'

    global_version_num = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    diagnoses_coefs = Column(String, nullable=False)

    def __init__(self, company_id, diagnoses_coefs):
        self.company_id = company_id
        self.diagnoses_coefs = diagnoses_coefs
