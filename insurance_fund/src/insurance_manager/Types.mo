import HashMap "mo:base/HashMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Nat "mo:base/Nat";
import Float "mo:base/Float";

module Types {
    public class InsurersData() {
        let map = HashMap.HashMap<InsurerWalletAddress, InsurerInfo>(16, Principal.equal, Principal.hash);

        public func put(key: InsurerWalletAddress, value: InsurerInfo): () {
            value.addTokens(60);
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
}
