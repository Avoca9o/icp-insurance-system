import Nat8 "mo:base/Nat8";
import Nat64 "mo:base/Nat64";
import Principal "mo:base/Principal";
import Blob "mo:base/Blob";

module {
    public type Account = {
        owner: Principal;
        subaccount: ?[Nat8];
    };

    public type TransferArgs = {
        from: Account;
        to: Account;
        amount: Nat;
        fee: ?Nat;
        memo: ?Blob;
        from_subaccount: ?[Nat8];
        created_at_time: ?Nat64;
    };

    public type Transaction = {
        block_index: Nat64;
        transfer: {
            amount: Nat64;
            from: Principal;
            to: Principal;
        };
    };

    public type GetTransactionsArgs = {
        account: Principal;
        start: Nat64;
        length: Nat;
    };
}; 