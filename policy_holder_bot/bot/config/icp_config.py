import os
from dotenv import load_dotenv

load_dotenv()

ICP_CANISTER_ID = os.getenv('ICP_CANISTER_ID')
ICP_CANISTER_URL = os.getenv('ICP_CANISTER_URL')

candid='''
type http_request_result = 
 record {
   body: blob;
   headers: vec http_header;
   status: nat;
 };
type http_header = 
 record {
   name: text;
   value: text;
 };
type Result_4 = 
 variant {
   err: text;
   ok: nat;
 };
type Result_3 = 
 variant {
   err: text;
   ok: opt Checksum;
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
type Checksum = text;
service : {
  add_approved_client: (InsurerWalletAddress, nat, Checksum) -> (Result);
  get_balance_from_ledger: (principal) -> (Result_4);
  get_checksum: (InsurerWalletAddress, nat) -> (Result_3);
  get_insurer_balance: (InsurerWalletAddress) -> (Result_2) query;
  refresh_balance: (InsurerWalletAddress) -> (Result_1);
  register_insurer: (InsurerWalletAddress) -> (Result);
  request_payout: (text, text, text, principal, principal, nat64, text) ->
   (Result_1);
  send_icp_tokens: (principal, nat64) -> (Result);
  transform: (record {
                context: blob;
                response: http_request_result;
              }) -> (http_request_result) query;
  withdraw: (InsurerWalletAddress) -> (Result);
}
'''
