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

import Types "Types";

actor {
    let insurers_data = HashMap.HashMap<Types.InsurerWalletAddress, Types.InsurerTokensAmount>(16, Principal.equal, Principal.hash);

    public func register_insurer(wallet_address: Types.InsurerWalletAddress) : async () {
        insurers_data.put(wallet_address, 0);
    };

    public query func get_insurer_balance(wallet_address: Types.InsurerWalletAddress): async ?Types.InsurerTokensAmount {
        return insurers_data.get(wallet_address)
    };

    public func top_up_insurer(wallet_address: Types.InsurerWalletAddress, amount: Nat): async ?() {
        do ? {
            insurers_data.get(wallet_address)!.addTokens(amount)
        };
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

    public func get_insurance_case_info() : async Bool {
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

        response_status == 200;
    };
}
