import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

Base = declarative_base()
