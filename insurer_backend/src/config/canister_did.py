candid="""
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
type Result_3 = 
 variant {
   err: text;
   ok: Checksum;
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
type InsuranceManager = 
 service {
   add_approved_client: (insurer: principal, client_id: nat, checksum:
    text) -> (Result_1);
   get_checksum: (insurer: InsurerWalletAddress, client_id: nat) ->
    (Result_3) query;
   get_insurer_balance: (wallet_address: principal) -> (Result_2);
   refresh_all: () -> ();
   refresh_balance: (wallet_address: principal) -> (Result);
   register_insurer: (wallet_address: principal) -> (Result_1);
   request_payout: (policy_number: text, diagnosis_code: text,
    diagnosis_date: text, insurer_crypto_wallet: principal,
    policy_holder_crypto_wallet: principal, amount: nat, oauth_token:
    text) -> (Result);
   transform: (record {
                 context: blob;
                 response: http_request_result;
               }) -> (http_request_result) query;
   withdraw: (wallet_address: InsurerWalletAddress) -> (Result);
 };
type Checksum = text;
service : () -> InsuranceManager
"""
