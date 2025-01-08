import HashMap "mo:base/HashMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Nat "mo:base/Nat";
import Float "mo:base/Float";

module Types {
    public class InsurersData() {
        let map = HashMap.HashMap<InsurerWalletAddress, InsurerInfo>(16, Principal.equal, Principal.hash);

        public func put(key: InsurerWalletAddress, value: InsurerInfo): () {
            map.put(key, value);
        };

        public func get(key: InsurerWalletAddress): ?Nat {
            return do ? {((map.get(key))!).getTokenBalance()};
        };

        public func keys(): [InsurerWalletAddress] {
            return Iter.toArray(map.keys());
        };
    };

    public class InsurerInfo(initialBalance: Nat) {
        var tokenBalance: Nat = initialBalance;

        let coefficients = HashMap.HashMap<DamageId, Float>(16, Principal.equal, Principal.hash);

        public func put(key: DamageId, value: Float): () {
            coefficients.put(key, value);
        };

        public func get(key: DamageId): ?Float {
            return coefficients.get(key);
        };

        public func keys(): [DamageId] {
            return Iter.toArray(coefficients.keys());
        };

        public func entries(): Iter.Iter<(DamageId, Float)> {
            return coefficients.entries();
        };

        public func getTokenBalance(): Nat {
            return tokenBalance;
        };

        public func addTokens(amount: Nat): () {
            tokenBalance += amount;
        };
    };

    public type InsurerWalletAddress = Principal;

    public type DamageId = Principal;

    public type Timestamp = Nat64;

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
