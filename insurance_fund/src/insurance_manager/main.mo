import ICPIndex "canister:icp_index_canister";
import ICPLedger "canister:icp_ledger_canister";
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

import Types "Types";

actor {
    let insurers_data = Types.InsurersData();

    public func register_insurer(wallet_address: Types.InsurerWalletAddress) : async Result.Result<(), Text> {
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

    public query func get_insurer_balance(wallet_address: Types.InsurerWalletAddress): async Result.Result<Types.InsurerTokensAmount, Text> {
        try {
            let insurer_balance = insurers_data.get_balance(wallet_address);
            switch(insurer_balance) {
                case(null) {
                    return #err("Insurer does not exist");
                };
                case(?insurer_balance) {
                    return #ok(insurer_balance);
                };
            }
        } catch (error) {
            return #err(Error.message(error));
        }
    };

    public func refresh(wallet_address: Types.InsurerWalletAddress): async Result.Result<Text, Text> {
        try {
            let insurer_amount = insurers_data.get_balance(wallet_address);
            if (insurer_amount == null) {
                return #err("Insurer does not exist");
            };

            let last_transaction = insurers_data.get_last_transaction(wallet_address);

            let insurer_transactions = await ICPIndex.get_account_transactions({
                max_results=10;
                start=null;
                account={
                    owner=wallet_address;
                    subaccount=null;
                }
            });
            switch(insurer_transactions) {
                case(#Ok(insurer_transactions)) {
                    var i = 0;
                    let transactions = insurer_transactions.transactions;
                    while (i < transactions.size()) {
                        let operation = transactions[i].transaction.operation;
                        let transaction_id = transactions[i].id;
                        if (last_transaction != null and Option.get(last_transaction, 0: Types.InsurerLastTransactionId) == transaction_id) {
                            return #ok("Not BAM");
                        };
                        switch (operation) {
                            case (#Transfer(operation)) {
                                if (operation.to == "9a2a49e111a1acd073e9b85b752cb0d54e6c3401e285d5019f9efacc77a83af4") {
                                    insurers_data.set_balance(wallet_address, Option.get(insurer_amount, 0: Types.InsurerTokensAmount) + operation.amount.e8s);
                                    insurers_data.set_last_transaction(wallet_address, transaction_id);
                                    return #ok("BAM");
                                };
                            };
                            case _ {

                            };
                        };
                        i += 1;
                    };
                    return #err("Cannot find transaction");
                };
                case(#Err(insurer_transactions)) {
                    return #err("Error while listing transactions")
                }
            }
        } catch(error) {
            return #err(Error.message(error));
        }
    };

    private func refresh_all(): async () {
        let insurers = insurers_data.get_all_insurers();
        for (insurer in insurers) {
            let result = await refresh(insurer);
        }
    };

    public func get_balance_from_ledger(user: Principal): async Result.Result<Nat, Text> {
        try {
            let balance = await ICPLedger.icrc1_balance_of({
                owner=user;
                subaccount=null;
            });
            return #ok(balance);
        } catch (error) {
            return #err(Error.message(error));
        }
    };

    public func send_icp_tokens(recipient: Principal, payout: Nat64): async Result.Result<(), Text> {
        try {
            let transferResult = await ICPLedger.icrc1_transfer({
                to={
                    owner=recipient;
                    subaccount=null;
                };
                amount=Nat64.toNat(payout);
                fee=null;
                memo=null;
                from_subaccount=null;
                created_at_time=null;
            });

            switch (transferResult) {
                case(#Ok(results)) {
                    return #ok();
                };
                case(#Err(error)) {
                    return #err("Error in trasnfering tokens");
                }
            }
        } catch (error) {
            return #err(Error.message(error));
        }
    };

    public query func transform(raw : Types.TransformArgs) : async Types.CanisterHttpResponsePayload {
        let transformed : Types.CanisterHttpResponsePayload = {
            status = raw.response.status;
            body = raw.response.body;
            headers = [
                { name = "Content-Security-Policy"; value = "default-src 'self'" },
                { name = "Referrer-Policy"; value = "strict-origin" },
                { name = "Permission-Policy"; value = "geolocation=(self)" },
                { name = "Strict-Transport-Security"; value = "max-age=63072000" },
                { name = "X-Frame-Options"; value = "DENY" },
                { name = "X-Content-Type-Options"; value = "nosniff" },
            ];
        };
        transformed;
    };

    private func validate_insurance_case(diagnosis_code: Text, diagnosis_date: Text) : async Bool {
        let ic : Types.IC = actor ("aaaaa-aa");
        let ONE_MINUTE : Nat64 = 60;
        let host: Text = "example.com";
        let url = "https://" # host # "/";

        let request_headers = [];

        let transform_context : Types.TransformContext = {
            function = transform;
            context = Blob.fromArray([]);
        };

        let http_request : Types.HttpRequestArgs = {
            url = url;
            max_response_bytes = null;
            headers = request_headers;
            body = null;
            method = #get;
            transform = ?transform_context;
        };

        Cycles.add<system>(20_949_972_000);

        let http_response : Types.HttpResponsePayload = await ic.http_request(http_request);
        let response_status: Nat = http_response.status;
        let response_body: Blob = Blob.fromArray(http_response.body);
        let decoded_text: Text = switch (Text.decodeUtf8(response_body)) {
            case (null) {"No value returned"};
            case (?y) { y };
        };

        return response_status == 200;
    };

    public func request_payout(diagnosis_code: Text, diagnosis_date: Text, insurer_crypto_wallet: Principal, policy_holder_crypto_wallet: Principal, amount: Nat64): async Result.Result<Text, Text> {
        let validate_diagnosis_result = await validate_insurance_case(diagnosis_code, diagnosis_date);

        if (validate_diagnosis_result) {
            let transfer_result = await send_icp_tokens(policy_holder_crypto_wallet, amount);
            switch (transfer_result) {
                case (#Err(error)) {
                    return #err("Transfer trouble")
                };
                case (_) {
                    
                }
            };
            let current_amount = insurers_data.get_balance(insurer_crypto_wallet);
            if (current_amount != null) {
                if (Option.get(current_amount, 0: Types.InsurerTokensAmount) < amount + 10000) {
                    return #err("Insurer does not have enough money for transfer");
                };
                insurers_data.set_balance(insurer_crypto_wallet, Option.get(current_amount, 0: Types.InsurerTokensAmount) - amount - 10000);
            };
            return #ok("Transfer was approved");
        } else {
            return #err("Insurance case is not approved")
        };
    };

    let timer = Timer.recurringTimer(#seconds 60, refresh_all);
}
