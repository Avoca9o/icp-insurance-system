import Array "mo:base/Array";
import Blob "mo:base/Blob";
import Buffer "mo:base/Buffer";
import Debug "mo:base/Debug";
import Hash "mo:base/Hash";
import HashMap "mo:base/HashMap";
import Iter "mo:base/Iter";
import Nat "mo:base/Nat";
import Nat8 "mo:base/Nat8";
import Nat32 "mo:base/Nat32";
import Nat64 "mo:base/Nat64";
import Option "mo:base/Option";
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Text "mo:base/Text";

actor InsToken {
    private let name : Text = "Insurance Token";
    private let symbol : Text = "INS";
    private let decimals : Nat8 = 8;
    private let fee : Nat = 10_000;  // 0.0001 INS
    
    public type Account = {
        owner : Principal;
        subaccount : ?[Nat8];
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

    private func accountsEqual(a: Account, b: Account) : Bool {
        a.owner == b.owner and Option.equal(a.subaccount, b.subaccount, func(a: [Nat8], b: [Nat8]) : Bool {
            a == b
        })
    };

    private func accountHash(account: Account) : Hash.Hash {
        let principal_hash = Principal.hash(account.owner);
        switch (account.subaccount) {
            case (?subaccount) {
                let subaccount_hash = Array.foldLeft<Nat8, Nat32>(
                    subaccount,
                    0,
                    func (acc, x) { acc +% Nat32.fromNat(Nat8.toNat(x)) }
                );
                principal_hash +% subaccount_hash
            };
            case null { principal_hash };
        }
    };

    private let owner : Principal = Principal.fromText("43cc7-eee4i-b4tyu-qfapq-zmovy-v2se3-xct27-y2xgb-dgxr7-4yo4g-iqe");
    private var totalSupply: Nat = 0;
    private var balances = HashMap.HashMap<Account, Nat64>(0, func (a1: Account, a2: Account) : Bool { 
        Principal.equal(a1.owner, a2.owner)
    }, func (a: Account) : Hash.Hash { 
        accountHash(a)
    });
    private var transactions = HashMap.HashMap<Nat64, Transaction>(0, Nat64.equal, func (n: Nat64) : Hash.Hash { 
        Hash.hash(Nat64.toNat(n))
    });
    private var next_block_index: Nat64 = 0;

    public query func icrc1_name() : async Text { name };
    public query func icrc1_symbol() : async Text { symbol };
    public query func icrc1_decimals() : async Nat8 { decimals };
    public query func icrc1_fee() : async Nat { fee };
    public query func icrc1_total_supply() : async Nat { totalSupply };

    public query func icrc1_balance_of(account: Account) : async Nat {
        switch (balances.get(account)) {
            case (?balance) { Nat64.toNat(balance) };
            case (null) { 0 };
        }
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

    public func get_transactions(args: GetTransactionsArgs) : async { transactions: [Transaction]; oldest_tx_id: ?Nat64; archived_in_blocks: [Nat64] } {
        var result: [Transaction] = [];
        var i: Nat64 = args.start;
        let end = args.start + Nat64.fromNat(args.length);
        while (i < end) {
            switch (transactions.get(i)) {
                case (?tx) {
                    result := Array.append(result, [tx]);
                };
                case (null) {};
            };
            i += 1;
        };
        { transactions = result; oldest_tx_id = null; archived_in_blocks = [] }
    };

    public shared({ caller }) func icrc1_transfer(args: TransferArgs) : async Result.Result<Nat64, Text> {
        let from = { owner = caller; subaccount = args.from_subaccount };
        let to = args.to;
        let amount = Nat64.fromNat(args.amount);

        let from_balance = switch (balances.get(from)) {
            case (?balance) { balance };
            case (null) { return #err("Insufficient balance") };
        };

        if (from_balance < amount) {
            return #err("Insufficient balance");
        };

        balances.put(from, from_balance - amount);
        
        let to_balance = switch (balances.get(to)) {
            case (?balance) { balance };
            case (null) { 0 : Nat64 };
        };
        balances.put(to, to_balance + amount);

        let tx: Transaction = {
            block_index = next_block_index;
            transfer = {
                amount = amount;
                from = from.owner;
                to = to.owner;
            };
        };
        transactions.put(next_block_index, tx);
        next_block_index += 1;

        #ok(next_block_index - 1)
    };

    public shared({ caller }) func mint(account: Account, amount: Nat) : async Result.Result<(), Text> {
        if (caller != owner) {
            return #err("Unauthorized");
        };

        let mint_amount = Nat64.fromNat(amount);
        totalSupply += amount;

        switch (balances.get(account)) {
            case (?balance) {
                balances.put(account, balance + mint_amount);
            };
            case (null) {
                balances.put(account, mint_amount);
            };
        };

        #ok()
    };
};
