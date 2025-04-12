import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import Nat64 "mo:base/Nat64";
import HashMap "mo:base/HashMap";
import Iter "mo:base/Iter";
import Text "mo:base/Text";
import Error "mo:base/Error";

module Types {
    public class InsurersData() {
        private var balances = HashMap.HashMap<InsurerWalletAddress, InsurerTokensAmount>(0, Principal.equal, Principal.hash);
        private var last_txs = HashMap.HashMap<InsurerWalletAddress, Nat64>(0, Principal.equal, Principal.hash);
        private var clients = HashMap.HashMap<InsurerWalletAddress, HashMap.HashMap<Text, Checksum>>(0, Principal.equal, Principal.hash);

        public func get_balance(address: InsurerWalletAddress) : ?InsurerTokensAmount {
            balances.get(address)
        };

        public func set_balance(address: InsurerWalletAddress, amount: InsurerTokensAmount) {
            balances.put(address, amount);
        };

        public func get_last_tx(address: InsurerWalletAddress) : Nat64 {
            switch (last_txs.get(address)) {
                case (?tx) { tx };
                case (null) { 0 };
            }
        };

        public func set_last_tx(address: InsurerWalletAddress, tx: Nat64) {
            last_txs.put(address, tx);
        };

        public func get_all_insurers() : [InsurerWalletAddress] {
            Iter.toArray(balances.keys())
        };

        public func add_client(insurer: InsurerWalletAddress, client_id: Text, checksum: Checksum) {
            switch (clients.get(insurer)) {
                case (?client_map) {
                    client_map.put(client_id, checksum);
                };
                case (null) {
                    let new_client_map = HashMap.HashMap<Text, Checksum>(0, Text.equal, Text.hash);
                    new_client_map.put(client_id, checksum);
                    clients.put(insurer, new_client_map);
                };
            };
        };

        public func get_checksum(insurer: InsurerWalletAddress, client_id: Text) : ?Checksum {
            switch (clients.get(insurer)) {
                case (?client_map) {
                    client_map.get(client_id)
                };
                case (null) {
                    null
                };
            };
        };
    };

    public type InsurerWalletAddress = Principal;

    public type InsurerTokensAmount = Nat64;

    public type InsurerLastTransactionId = Nat64;

    public type PolicyHolderId = Text;

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

    public type Account = {
        owner: Principal;
        subaccount: ?[Nat8];
    };

    public type Transaction = {
        block_index: Nat64;
        transfer: {
            amount: Nat;
            from: Account;
            to: Account;
        };
    };

    public type GetTransactionsResponse = {
        transactions: [Transaction];
        oldest_tx_id: ?Nat64;
        archived_in_blocks: [Nat64];
    };
}
