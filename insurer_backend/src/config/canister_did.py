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
   add_approved_client: (InsurerWalletAddress, nat, Checksum) -> (Result_1);
   get_checksum: (InsurerWalletAddress, nat) -> (Result_3) query;
   get_insurer_balance: (principal) -> (Result_2);
   refresh_all: () -> ();
   refresh_balance: (principal) -> (Result);
   register_insurer: (principal) -> (Result_1);
   request_payout: (text, text, text, principal, principal,
    InsurerTokensAmount, text) -> (Result);
   transform: (record {
                 context: blob;
                 response: http_request_result;
               }) -> (http_request_result) query;
   withdraw: (InsurerWalletAddress) -> (Result);
 };
type Checksum = text;
service : () -> InsuranceManager
"""
