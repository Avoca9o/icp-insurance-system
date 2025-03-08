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

import IC "ic:aaaaa-aa";
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

    public func refresh_balance(wallet_address: Types.InsurerWalletAddress): async Result.Result<Text, Text> {
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
                            return #ok("The last saved transaction has been detected. The balance has been replenished.");
                        };
                        switch (operation) {
                            case (#Transfer(operation)) {
                                if (operation.to == "9a2a49e111a1acd073e9b85b752cb0d54e6c3401e285d5019f9efacc77a83af4") {
                                    insurers_data.set_balance(wallet_address, Option.get(insurer_amount, 0: Types.InsurerTokensAmount) + operation.amount.e8s);
                                    insurers_data.set_last_transaction(wallet_address, transaction_id);
                                };
                            };
                            case _ {

                            };
                        };
                        i += 1;
                    };
                    return #ok("The last saved transaction has not been detected. The balance has been replenished.");
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
            let result = await refresh_balance(insurer);
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

    public query func transform({
        context : Blob;
        response : IC.http_request_result;
    }) : async IC.http_request_result {
        {
            response with headers = []; // not intersted in the headers
        };
    };

    func generateUUID() : Text {
        "UUID-123456789";
    };

    private func get_oauth_token(): async Text {
        let host: Text = "127.0.0.1:8000";
        let url = "http://127.0.0.1:8000/open-data/v1.0/mfsp/token";

        let idempotency_key : Text = generateUUID();
        let request_headers = [
            { name = "User-Agent"; value = "http_post_sample" },
            { name = "Content-Type"; value = "application/json" },
            { name = "Idempotency-Key"; value = idempotency_key },
        ];

        let request_body_json : Text = "{ \"username\" : \"johndoe\", \"password\" : \"secret\" }";
        let request_body = Text.encodeUtf8(request_body_json); 

        let http_request : IC.http_request_args = {
            url = url;
            max_response_bytes = null;
            headers = request_headers;
            body = ?request_body;
            method = #post;
            transform = ?{
                function = transform;
                context = Blob.fromArray([]);
            };
        };

        Cycles.add<system>(20_949_972_000);

        let http_response: IC.http_request_result = await IC.http_request(http_request);
        let decoded_text: Text = switch (Text.decodeUtf8(http_response.body)) {
            case (null) {"No value returned"};
            case (?y) { y };
        };

        let tmp = Text.stripStart(decoded_text, #char '\"');
        let result = Text.stripEnd(Option.get(tmp, ""), #char '\"');
        return Option.get(result, "");
    };

    private func validate_insurance_case(policy_number: Text, diagnosis_code: Text, date: Text): async Bool {
        let host : Text = "127.0.0.1:8000";
        let url = "http://" # host # "/open-data/v1.0/mfsp/insurance-cases?policy_number=" # policy_number # "&diagnosis_code=" # diagnosis_code # "&date=" # date;

        let token = await get_oauth_token();
        let request_headers = [
            { name = "Authorization"; value = "Bearer " # token },
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

    public func request_payout(policy_number: Text, diagnosis_code: Text, diagnosis_date: Text, insurer_crypto_wallet: Principal, policy_holder_crypto_wallet: Principal, amount: Nat64): async Result.Result<Text, Text> {
        let validate_diagnosis_result = await validate_insurance_case(policy_number, diagnosis_code, diagnosis_date);

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

    public func withdraw(wallet_address: Types.InsurerWalletAddress): async Result.Result<(), Text> {
        try {
            let insurer_balance = insurers_data.get_balance(wallet_address);
            switch(insurer_balance) {
                case(null) {
                    return #err("Insurer does not exist");
                };
                case(_) {

                }
            };

            insurers_data.set_balance(wallet_address, 0);

            let transferResult = await ICPLedger.icrc1_transfer({
                to={
                    owner=wallet_address;
                    subaccount=null;
                };
                amount=Nat64.toNat(Option.get(insurer_balance, 0: Types.InsurerTokensAmount));
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
                    return #err("Error in withdraw operation");
                };
            };
        } catch (error) {
            return #err(Error.message(error));
        }
    };

    public func add_approved_client(insurer: Types.InsurerWalletAddress, client_id: Nat, checksum: Types.Checksum): async Result.Result<(), Text> {
        try {
            insurers_data.add_client(insurer, Nat.toText(client_id), checksum);
            return #ok();
        } catch (error) {
            return #err(Error.message(error));
        }
    };

    public func get_checksum(insurer: Types.InsurerWalletAddress, client_id: Nat): async Result.Result<?Types.Checksum, Text> {
        try{
            return #ok(insurers_data.get_checksum(insurer, Nat.toText(client_id)));
        } catch (error) {
            return #err(Error.message(error));
        }
    };

    let timer = Timer.recurringTimer(#seconds 60, refresh_all);
}
