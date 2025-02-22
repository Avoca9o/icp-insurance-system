import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Nat64 "mo:base/Nat64";
import HashMap "mo:base/HashMap";
import Iter "mo:base/Iter";
import Text "mo:base/Text";

module Types {
    public class InsurersData() {
        private let _balances = HashMap.HashMap<InsurerWalletAddress, InsurerTokensAmount>(16, Principal.equal, Principal.hash);
        private let _last_transactions = HashMap.HashMap<InsurerWalletAddress, InsurerLastTransactionId>(16, Principal.equal, Principal.hash);

        public func set_balance(insurer: InsurerWalletAddress, amount: InsurerTokensAmount): () {
            _balances.put(insurer, amount);
        };

        public func get_balance(insurer: InsurerWalletAddress): ?InsurerTokensAmount {
            return _balances.get(insurer);
        };

        public func get_all_insurers(): Iter.Iter<InsurerWalletAddress> {
            return _balances.keys();
        };

        public func set_last_transaction(insurer: InsurerWalletAddress, transaction_id: InsurerLastTransactionId): () {
            _last_transactions.put(insurer, transaction_id);
        };

        public func get_last_transaction(insurer: InsurerWalletAddress): ?InsurerLastTransactionId {
            return _last_transactions.get(insurer);
        };
    };

    public type InsurerWalletAddress = Principal;

    public type InsurerTokensAmount = Nat64;

    public type InsurerLastTransactionId = Nat64;

    public type DamageId = Principal;

    public type Timestamp = Nat64;

    public type HttpRequestArgs = {
        url : Text;
        max_response_bytes : ?Nat64;
        headers : [HttpHeader];
        body : ?Blob;
        method : HttpMethod;
        transform : ?TransformRawResponseFunction;
    };

    public type HttpHeader = {
        name: Text;
        value : Text;
    };

    public type HttpMethod = {
        #get;
        #post;
        #head;
    };

    public type HttpResponsePayload = {
        status : Nat;
        headers : [HttpHeader];
        body : [Nat8];
    };

    public type TransformRawResponseFunction = {
        function : shared query TransformArgs -> async HttpResponsePayload;
        context : Blob;
    };

    public type TransformArgs = {
        response : HttpResponsePayload;
        context : Blob;
    };

    public type CanisterHttpResponsePayload = {
        status : Nat;
        headers : [HttpHeader];
        body : [Nat8];
    };

    public type TransformContext = {
        function : shared query TransformArgs -> async HttpResponsePayload;
        context : Blob;
    };

    public type IC = actor {
        http_request: HttpRequestArgs -> async HttpResponsePayload;
    };
}
