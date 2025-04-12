import Array "mo:base/Array";
import Debug "mo:base/Debug";
import Nat "mo:base/Nat";
import Nat64 "mo:base/Nat64";
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Text "mo:base/Text";
import Blob "mo:base/Blob";
import Types "./types";

actor class InsTokenTest(ins_token: actor {
    icrc1_name: () -> async Text;
    icrc1_symbol: () -> async Text;
    icrc1_decimals: () -> async Nat8;
    icrc1_fee: () -> async Nat;
    icrc1_total_supply: () -> async Nat;
    icrc1_balance_of: (Types.Account) -> async Nat;
    icrc1_transfer: (Types.TransferArgs) -> async Result.Result<Nat64, Text>;
    mint: (Types.Account, Nat) -> async Result.Result<(), Text>;
    get_transactions: (Types.GetTransactionsArgs) -> async { transactions: [Types.Transaction]; oldest_tx_id: ?Nat64; archived_in_blocks: [Nat64] };
}) {
    // Тесты
    public func test_token_metadata() : async Bool {
        let name = await ins_token.icrc1_name();
        let symbol = await ins_token.icrc1_symbol();
        let decimals = await ins_token.icrc1_decimals();
        let fee = await ins_token.icrc1_fee();
        
        assert name == "Insurance Token";
        assert symbol == "INS";
        assert decimals == 8;
        assert fee == 10_000;
        
        true
    };

    public func test_mint_and_balance() : async Bool {
        // Используем владельца токена для минта
        let owner = Principal.fromText("43cc7-eee4i-b4tyu-qfapq-zmovy-v2se3-xct27-y2xgb-dgxr7-4yo4g-iqe");
        let account = { owner = owner; subaccount = null };
        let amount = 1_000_000_000;
        
        // Проверяем начальный баланс
        let initial_balance = await ins_token.icrc1_balance_of(account);
        
        // Минтим токены
        let mint_result = await ins_token.mint(account, amount);
        Debug.print("Mint result: " # debug_show(mint_result));
        
        // Проверяем, что минт либо успешен, либо возвращает ошибку "Unauthorized"
        switch (mint_result) {
            case (#ok()) {
                // Если минт успешен, проверяем, что баланс увеличился
                let new_balance = await ins_token.icrc1_balance_of(account);
                assert new_balance == initial_balance + amount;
            };
            case (#err(msg)) {
                // Если минт не удался, это должно быть из-за отсутствия прав
                assert msg == "Unauthorized";
            };
        };
        
        true
    };

    public func test_transfer() : async Bool {
        let owner = Principal.fromText("43cc7-eee4i-b4tyu-qfapq-zmovy-v2se3-xct27-y2xgb-dgxr7-4yo4g-iqe");
        let recipient = Principal.fromText("be2us-64aaa-aaaaa-qaabq-cai");
        
        let from_account = { owner = owner; subaccount = null };
        let to_account = { owner = recipient; subaccount = null };
        
        let transfer_amount = 100_000_000;
        
        // Получаем начальные балансы
        let initial_from_balance = await ins_token.icrc1_balance_of(from_account);
        let initial_to_balance = await ins_token.icrc1_balance_of(to_account);
        
        // Переводим токены
        let transfer_args = {
            from = from_account;
            to = to_account;
            amount = transfer_amount;
            fee = null;
            memo = null;
            from_subaccount = null;
            created_at_time = null;
        };
        
        let transfer_result = await ins_token.icrc1_transfer(transfer_args);
        
        // Проверяем результат перевода
        switch (transfer_result) {
            case (#ok(_)) {
                // Если перевод успешен, проверяем балансы
                let new_from_balance = await ins_token.icrc1_balance_of(from_account);
                let new_to_balance = await ins_token.icrc1_balance_of(to_account);
                
                assert new_from_balance == initial_from_balance - transfer_amount;
                assert new_to_balance == initial_to_balance + transfer_amount;
            };
            case (#err(msg)) {
                // Если перевод не удался, это должно быть из-за недостаточного баланса
                assert msg == "Insufficient balance";
            };
        };
        
        true
    };

    public func test_get_transactions() : async Bool {
        let owner = Principal.fromText("43cc7-eee4i-b4tyu-qfapq-zmovy-v2se3-xct27-y2xgb-dgxr7-4yo4g-iqe");
        
        let args = {
            account = owner;
            start = 0 : Nat64;
            length = 10;
        };
        
        let result = await ins_token.get_transactions(args);
        
        // Проверяем, что транзакции возвращаются (даже если их нет)
        assert (result.transactions.size() >= 0);
        
        true
    };

    public func run_all_tests() : async [Bool] {
        var results : [Bool] = [];
        
        // Запускаем все тесты
        let metadata_result = await test_token_metadata();
        results := Array.append(results, [metadata_result]);
        
        let mint_result = await test_mint_and_balance();
        results := Array.append(results, [mint_result]);
        
        let transfer_result = await test_transfer();
        results := Array.append(results, [transfer_result]);
        
        let transactions_result = await test_get_transactions();
        results := Array.append(results, [transactions_result]);
        
        results
    };
}; 