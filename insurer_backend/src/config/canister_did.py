candid="""
type TransformArgs = 
 record {
   context: blob;
   response: HttpResponsePayload;
 };
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
  get_insurance_case_info: () -> (bool);
  transform: (TransformArgs) -> (CanisterHttpResponsePayload) query;
}
"""