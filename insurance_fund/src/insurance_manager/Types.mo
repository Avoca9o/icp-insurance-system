import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Nat64 "mo:base/Nat64";
import HashMap "mo:base/HashMap";
import Iter "mo:base/Iter";

module Types {
    public class InsurersData() {
        private let _insurers_info = HashMap.HashMap<InsurerWalletAddress, InsurerInfo>(16, Principal.equal, Principal.hash);

        public func set_balance(insurer: InsurerWalletAddress, amount: InsurerTokensAmount): () {
            let insurer_info: ?InsurerInfo = _insurers_info.get(insurer);
            switch(insurer_info) {
                case(null) {
                    let new_insurer_info: InsurerInfo = InsurerInfo();
                    new_insurer_info.set_balance(amount);
                    _insurers_info.put(insurer, new_insurer_info);
                };
                case(?insurer_info) {
                    insurer_info.set_balance(amount);
                    _insurers_info.put(insurer, insurer_info);
                }
            }
        };

        public func get_balance(insurer: InsurerWalletAddress): ?InsurerTokensAmount {
            let insurer_info: ?InsurerInfo = _insurers_info.get(insurer);
            switch(insurer_info) {
                case(null) {
                    return null;
                };
                case(?insurer_info) {
                    return ?insurer_info.get_balance();
                }
            }
        };

        public func get_all_insurers(): Iter.Iter<InsurerWalletAddress> {
            return _insurers_info.keys();
        };

        public func set_last_transaction(insurer: InsurerWalletAddress, transaction_id: InsurerLastTransactionId): () {
            let insurer_info: ?InsurerInfo = _insurers_info.get(insurer);
            switch(insurer_info) {
                case(null) {
                    let new_insurer_info: InsurerInfo = InsurerInfo();
                    new_insurer_info.set_last_transaction(transaction_id);
                    _insurers_info.put(insurer, new_insurer_info);
                };
                case(?insurer_info) {
                    insurer_info.set_last_transaction(transaction_id);
                    _insurers_info.put(insurer, insurer_info);
                }
            }
        };

        public func get_last_transaction(insurer: InsurerWalletAddress): ?InsurerLastTransactionId {
            let insurer_info: ?InsurerInfo = _insurers_info.get(insurer);
            switch(insurer_info) {
                case(null) {
                    return null;
                };
                case(?insurer_info) {
                    return ?insurer_info.get_last_transaction();
                }
            }
        };

        public func has_approved_clients(insurer: InsurerWalletAddress): Bool {
            let insurer_info: ?InsurerInfo = _insurers_info.get(insurer);
            switch(insurer_info) {
                case(null) {
                    return false;
                };
                case(?insurer_info) {
                    return insurer_info.get_approved_clients_number() == 0;
                }
            }
        }
    };

    public class InsurerInfo() {
        private var _balance: InsurerTokensAmount = 0;
        private var _last_transaction: InsurerLastTransactionId = 0;
        private let _policy_holders = HashMap.HashMap<PolicyHolderWalletAddress, Checksum>(16, Principal.equal, Principal.hash);

        public func get_balance(): InsurerTokensAmount {
            return _balance;
        };

        public func set_balance(new_balance: InsurerTokensAmount): () {
            _balance := new_balance;
        };

        public func get_last_transaction(): InsurerTokensAmount {
            return _last_transaction;
        };

        public func set_last_transaction(new_last_transaction: InsurerLastTransactionId): () {
            _last_transaction := new_last_transaction;
        };

        public func get_checksum(wallet_address: PolicyHolderWalletAddress): ?Checksum {
            return _policy_holders.get(wallet_address);
        };

        public func set_checksum(wallet_address: PolicyHolderWalletAddress, checksum: Checksum): () {
            _policy_holders.put(wallet_address, checksum);
        };

        public func get_approved_clients_number(): Nat {
            return _policy_holders.size();
        }
    };

    public type InsurerWalletAddress = Principal;

    public type InsurerTokensAmount = Nat64;

    public type InsurerLastTransactionId = Nat64;

    public type PolicyHolderWalletAddress = Principal;

    public type Checksum = Text;

    public type HttpRequestArgs = {
        url : Text;
        max_response_bytes : ?Nat64;
        headers : [HttpHeader];
        body : ?[Nat8];
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
