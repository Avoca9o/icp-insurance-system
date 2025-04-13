import ICPIndex "canister:icp_index_canister";
import InsToken "canister:ins_token";
import Debug "mo:base/Debug";
import Blob "mo:base/Blob";
import Cycles "mo:base/ExperimentalCycles";
import Error "mo:base/Error";
import Array "mo:base/Array";
import Nat8 "mo:base/Nat8";
import Nat64 "mo:base/Nat64";
import Text "mo:base/Text";
import Result "mo:base/Result";
import Principal "mo:base/Principal";
import Nat "mo:base/Nat";
import HashMap "mo:base/HashMap";
import Hash "mo:base/Hash";
import Bool "mo:base/Bool";
import Option "mo:base/Option";
import Timer "mo:base/Timer";
import Iter "mo:base/Iter";

import IC "ic:aaaaa-aa";
import Types "Types";

actor class InsuranceManager() {
    let insurers_data = Types.InsurersData();
    private let owner: Principal = Principal.fromText("2vxsx-fae");
    private var approved_users = HashMap.HashMap<Principal, Bool>(0, Principal.equal, Principal.hash);

    public func register_insurer(wallet_address: Principal) : async Result.Result<(), Text> {
        try {
            let insurer = insurers_data.get_balance(wallet_address);
            switch(insurer) {
                case(null) {
                    insurers_data.set_balance(wallet_address, 0);
                    return #ok();
                };
                case(?insurer) {
                    return #err("Insurer already exists");
                }
            }
        } catch(error) {
            return #err(Error.message(error));
        }
    };

    public func get_insurer_balance(wallet_address: Principal): async Result.Result<Types.InsurerTokensAmount, Text> {
        try {
            let account = {
                owner = wallet_address;
                subaccount = null;
            };
            let balance = await InsToken.icrc1_balance_of(account);
            return #ok(Nat64.fromNat(balance));
        } catch (error) {
            return #err(Error.message(error));
        }
    };

    public func refresh_balance(wallet_address: Principal): async Result.Result<Text, Text> {
        try {
            let last_tx = insurers_data.get_last_tx(wallet_address);
            let account = {
                owner = wallet_address;
                subaccount = null;
            };
            let transactions = await InsToken.get_transactions({
                account = wallet_address;
                start = last_tx;
                length = 100;
            });
            
            var new_balance : Nat64 = switch (insurers_data.get_balance(wallet_address)) {
                case (?balance) { balance };
                case (null) { 0 };
            };

            for (tx in transactions.transactions.vals()) {
                if (tx.block_index > last_tx) {
                    if (Principal.equal(tx.transfer.to, wallet_address)) {
                        new_balance := new_balance + tx.transfer.amount;
                    } else if (Principal.equal(tx.transfer.from, wallet_address)) {
                        new_balance := new_balance - tx.transfer.amount;
                    };
                    insurers_data.set_last_tx(wallet_address, tx.block_index);
                };
            };
            
            insurers_data.set_balance(wallet_address, new_balance);
            return #ok("Balance refreshed successfully");
        } catch(error) {
            return #err(Error.message(error));
        }
    };

    public shared(msg) func send_tokens(recipient: Principal, amount: Types.InsurerTokensAmount): async Result.Result<(), Text> {
        try {
            let transferResult = await InsToken.icrc1_transfer({
                to = {
                    owner = recipient;
                    subaccount = null;
                };
                amount = Nat64.toNat(amount);
                fee = null;
                memo = null;
                from_subaccount = null;
                created_at_time = null;
                from = {
                    owner = msg.caller;
                    subaccount = null;
                };
            });

            switch (transferResult) {
                case (#ok(_)) { return #ok(); };
                case (#err(e)) { return #err("Error in transferring tokens: " # e); };
            }
        } catch (error) {
            return #err(Error.message(error));
        }
    };

    public func request_payout(policy_number: Text, diagnosis_code: Text, diagnosis_date: Text, insurer_crypto_wallet: Principal, policy_holder_crypto_wallet: Principal, amount: Types.InsurerTokensAmount, oauth_token: Text): async Result.Result<Text, Text> {
        let validate_diagnosis_result = await validate_insurance_case(policy_number, diagnosis_code, diagnosis_date, oauth_token);

        if (not validate_diagnosis_result) {
            return #err("Invalid insurance case");
        };

        let transferResult = await InsToken.icrc1_transfer({
            to = {
                owner = policy_holder_crypto_wallet;
                subaccount = null;
            };
            amount = Nat64.toNat(amount);
            fee = null;
            memo = null;
            from_subaccount = null;
            created_at_time = null;
            from = {
                owner = insurer_crypto_wallet;
                subaccount = null;
            };
        });

        switch (transferResult) {
            case (#ok(_)) { return #ok("Payout successful"); };
            case (#err(e)) { return #err("Error in payout operation: " # e); };
        };
    };

    public query func transform({
        context : Blob;
        response : IC.http_request_result;
    }) : async IC.http_request_result {
        {
            response with headers = [];
        };
    };

    func generateUUID() : Text {
        "UUID-123456789";
    };

    private func validate_insurance_case(policy_number: Text, diagnosis_code: Text, date: Text, oauth_token: Text): async Bool {
        let host : Text = "127.0.0.1:8000";
        let url = "http://" # host # "/open-data/v1.0/mfsp/insurance-cases?policy_number=" # policy_number # "&diagnosis_code=" # diagnosis_code # "&date=" # date;

        let request_headers = [
            { name = "Authorization"; value = "Bearer " # oauth_token },
        ];

        let http_request : IC.http_request_args = {
            url = url;
            max_response_bytes = null;
            headers = request_headers;
            body = null;
            method = #get;
            transform = ?{
                function = transform;
                context = Blob.fromArray([]);
            };
        };

        Cycles.add<system>(230_949_972_000);

        let http_response : IC.http_request_result = await IC.http_request(http_request);
        return http_response.status == 200;
    };

    public shared(msg) func refresh_all() : async () {
        let insurers = insurers_data.get_all_insurers();
        for (address in Array.vals(insurers)) {
            let _ = await refresh_balance(address);
        };
    };

    public shared(msg) func withdraw_amount(amount : Nat64) : async Result.Result<(), Text> {
        let caller = msg.caller;
        switch (insurers_data.get_balance(caller)) {
            case (null) { #err("No balance found for this address") };
            case (?balance) {
                if (balance < amount) {
                    #err("Insufficient balance")
                } else {
                    let new_balance = balance - amount;
                    insurers_data.set_balance(caller, new_balance);
                    #ok()
                }
            };
        };
    };

    private func refresh_all_wrapper() : async () {
        await refresh_all();
    };

    let timer = Timer.recurringTimer<system>(#seconds 60, refresh_all_wrapper);

    public shared(msg) func add_approved_user(user: Principal) : async Result.Result<(), Text> {
        if (msg.caller == owner) {
            approved_users.put(user, true);
            return #ok();
        } else {
            return #err("Unauthorized");
        };
    };

    public query func is_user_approved(user: Principal) : async Bool {
        switch (approved_users.get(user)) {
            case (?approved) { approved };
            case (null) { false };
        };
    };
}
