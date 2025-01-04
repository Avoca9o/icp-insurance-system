import Types "Types"

actor {
    let map = Types.InsurersData();

    public func put(address: Types.InsurerWalletAddress): async Bool {
        map.put(address, Types.InsurerInfo(0));
        return true;
    };

    public func get(address: Types.InsurerWalletAddress): async ?Nat {
        return map.get(address);
    };
};
