import HashMap "mo:base/HashMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Nat "mo:base/Nat";
import Float "mo:base/Float";
import Text "mo:base/Text";

module Types {
    public class PolicyHoldersData() {
        let map = HashMap.HashMap<PolicyHolderUUID, PolicyHolderInfo>(16, Text.equal, Text.hash);

        public func put(key: PolicyHolderUUID, value: PolicyHolderInfo): () {
            map.put(key, value);
        };

        public func get(key: PolicyHolderUUID): ?Nat {
            return do ? {((map.get(key))!).getInsuranceAmount()};
        };

        public func keys(): [PolicyHolderUUID] {
            return Iter.toArray(map.keys());
        };
    };

    public class PolicyHolderInfo(initialAmount: Nat, address: PolicyHolderWalletAddress, insuranceCompany: InsurerWalletAddress) {
        var insuranceAmount: Nat = initialAmount;

        var walletAddress: PolicyHolderWalletAddress = address;

        var insurer: InsurerWalletAddress = insuranceCompany;

        let personalCoefficients = HashMap.HashMap<DamageId, Float>(16, Principal.equal, Principal.hash);

        public func put(key: DamageId, value: Float): () {
            personalCoefficients.put(key, value);
        };

        public func get(key: DamageId): ?Float {
            return personalCoefficients.get(key);
        };

        public func keys(): [DamageId] {
            return Iter.toArray(personalCoefficients.keys());
        };

        public func entries(): Iter.Iter<(DamageId, Float)> {
            return personalCoefficients.entries();
        };

        public func getInsuranceAmount(): Nat {
            return insuranceAmount;
        };
    };

    public type InsurerWalletAddress = Principal;

    public type PolicyHolderWalletAddress = Principal;

    public type PolicyHolderUUID = Text;

    public type DamageId = Principal;
}