import os
from dotenv import load_dotenv
from ic.canister import Canister
from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import Types
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
ICP_CANISTER_ID = os.getenv('ICP_CANISTER_ID')
ICP_CANISTER_URL = os.getenv('ICP_CANISTER_URL')

Base = declarative_base()

candid='''
type TransformArgs = 
 record {
   context: blob;
   response: HttpResponsePayload;
 };
type Result_3 = 
 variant {
   err: text;
   ok: nat;
 };
type Result_2 = 
 variant {
   err: text;
   ok: InsurerTokensAmount;
 };
type Result_1 = 
 variant {
   err: text;
   ok;
 };
type Result = 
 variant {
   err: text;
   ok: text;
 };
type InsurerWalletAddress = principal;
type InsurerTokensAmount = nat64;
type HttpResponsePayload = 
 record {
   body: vec nat8;
   headers: vec HttpHeader;
   status: nat;
 };
type HttpHeader = 
 record {
   name: text;
   value: text;
 };
type CanisterHttpResponsePayload = 
 record {
   body: vec nat8;
   headers: vec HttpHeader;
   status: nat;
 };
service : {
  get_balance_from_ledger: (principal) -> (Result_3);
  get_insurer_balance: (InsurerWalletAddress) -> (Result_2) query;
  register_insurer: (InsurerWalletAddress) -> (Result_1);
  send_icp_tokens: (principal, nat) -> (Result_1);
  top_up_insurer: (InsurerWalletAddress) -> (Result);
  transform: (TransformArgs) -> (CanisterHttpResponsePayload) query;
  validate_insurance_case: (principal) -> (Result);
}
'''
