from sqlalchemy import Column, ForeignKey, Integer, String

from bot.config.db_config import Base

class InsurerScheme(Base):
    __tablename__ = 'insurer_schemas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    global_version_num = Column(Integer, unique=True)
    version = Column(Integer)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    diagnoses_coefs = Column(String, nullable=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
