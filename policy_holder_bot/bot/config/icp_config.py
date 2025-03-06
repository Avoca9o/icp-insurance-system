import os
from dotenv import load_dotenv

load_dotenv()

ICP_CANISTER_ID = os.getenv('ICP_CANISTER_ID')
ICP_CANISTER_URL = os.getenv('ICP_CANISTER_URL')

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
   ok: text;
 };
type Result = 
 variant {
   err: text;
   ok;
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
  request_payout: (text, text, principal, principal, nat64) -> (Result_1);
}
'''
