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

import Types "Types";

actor {
    let insurers_data = HashMap.HashMap<Types.InsurerWalletAddress, Types.InsurerTokensAmount>(16, Principal.equal, Principal.hash);
    let insurers_top_up_info = HashMap.HashMap<Types.InsurerWalletAddress, Types.InsurerLastTransactionId>(16, Principal.equal, Principal.hash);

    public func register_insurer(wallet_address: Types.InsurerWalletAddress) : async Result.Result<(), Text> {
        try {
            let insurer = insurers_data.get(wallet_address);
            switch(insurer) {
                case(null) {
                    insurers_data.put(wallet_address, 0);
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
            let insurer_balance = insurers_data.get(wallet_address);
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

    public func top_up_insurer(wallet_address: Types.InsurerWalletAddress): async Result.Result<Text, Text> {
        try {
            let insurer = insurers_data.get(wallet_address);
            if (insurer == null) {
                return #err("Insurer does not exist");
            };

            let last_transaction = insurers_top_up_info.get(wallet_address);

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
                        if (last_transaction != null and last_transaction == transaction_id) {
                            return #ok("Not BAM");
                        };
                        switch (operation) {
                            case (#Transfer(operation)) {
                                if (operation.to == "d0f2d8256377109703c1440adfa4b57aee61084b62d2ecaa6308b9c1cf69f10f") {
                                    insurers_data.put(wallet_address, operation.amount.e8s);
                                    insurers_top_up_info.put(wallet_address, transaction_id);
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

    public func send_icp_tokens(recipient: Principal, payout: Nat): async Result.Result<(), Text> {
        try {
            let transferResult = await ICPLedger.icrc1_transfer({
                to={
                    owner=recipient;
                    subaccount=null;
                };
                amount=payout;
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

    public func validate_insurance_case(policy_holder: Principal) : async Result.Result<Text, Text> {
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

        if (response_status == 200) {
            let result = await send_icp_tokens(policy_holder, 1000000);
            return #ok("Tokens sent to policy holder");
        } else {
            return #err("Insurance case is not approved");
        }
    };
}
