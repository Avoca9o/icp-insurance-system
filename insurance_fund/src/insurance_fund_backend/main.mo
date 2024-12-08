import Nat8 "mo:base/Nat8";
import Debug "mo:base/Debug";
import Blob "mo:base/Blob";
import Nat "mo:base/Nat";

import IC "ic:aaaaa-aa";
import Timer "mo:base/Timer";
import Cycles "mo:base/ExperimentalCycles";
import Text "mo:base/Text";
import Types "Types";

actor {
  stable var currentRandomNumber : Nat = 0;
  stable var proposalId : Text = "1";

  private func generateNewNumber() : async () {
    let randomBytes = await IC.raw_rand();
    if (randomBytes.size() > 0) {
      let bytes : [Nat8] = Blob.toArray(randomBytes);
      currentRandomNumber := Nat8.toNat(bytes[0]) + 133000;
      Debug.print("Generated new random number: " # Nat.toText(currentRandomNumber));
      proposalId := Nat.toText(currentRandomNumber);
    };
  };

  public query func getCurrentNumber() : async Nat {
    currentRandomNumber
  };

  public func getIcpInfo() : async Text {
    let url = "https://example.com/";
    let transform_context : Types.TransformContext = {
      function = transform;
      context = Blob.fromArray([]);
    };
    let http_request = {
      url = url;
      max_response_bytes = null;
      headers = [];
      body = null;
      method = #get;
      transform = ?transform_context;
    };

    Cycles.add<system>(20_949_972_000);

    let http_response = await IC.http_request(http_request);

    let response_body: Blob = http_response.body;
    switch (Text.decodeUtf8(response_body)) {
      case null { "Null value returned" };
      case (?y) {y};
    };
  };

  public query func transform(raw : Types.TransformArgs) : async IC.http_request_result {
    {
      status = raw.response.status;
      body = raw.response.body;
      headers = [ ];
    };
  };

  private func printResults() : async () {
    Debug.print("Generated new random proposal number: " # Nat.toText(currentRandomNumber));
    let result : Text = await getIcpInfo();
    Debug.print("Proposal info obtained through HTTPS outcall: " # result);
  };

  let timer1 = Timer.recurringTimer<system>(#seconds 30, generateNewNumber);
  let timer2 = Timer.recurringTimer<system>(#seconds 32, printResults);
}