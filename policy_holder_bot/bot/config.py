import os
from dotenv import load_dotenv
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import Types
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
# DATABASE_URL = os.getenv('DATABASE_URL')
# ICP_CANISTER_ID = os.getenv('ICP_CANISTER_ID')
# ICP_CANISTER_URL = os.getenv('ICP_CANISTER_URL')

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# candid=''

# identity = Identity()
# client = Client(url=ICP_CANISTER_URL)
# agent = Agent(identity, client)
# canister = Canister(agent=agent, canister_id=ICP_CANISTER_ID, candid=candid)
