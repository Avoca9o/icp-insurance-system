import React, { useState } from "react";
import { fetchApi } from "../../services/Api";
import buttonStyle from "../../styles/ButtonStyle";

const BalanceController = () => {
    const [balance, setBalance] = useState(null);
    const [address, setAddress] = useState(null);

    const getBalance = async () => {
      try {
        const data = await fetchApi("/v1/balance", "GET");
        setBalance(data.message);
      } catch (error) {
        alert("Error retrieving balance: " + error.message);
      }
    };

    const getICPAddress = async () => {
      try {
        const data = await fetchApi("/v1/icp-address", "GET");
        setAddress(data.icp_address);
      } catch (error) {
        alert("Error retrieving ICP address: " + error.message);
      }
    };

    const withdraw = async () => {
      try {
        await fetchApi("/v1/withdraw", "POST");
        alert("Funds withdrawn successfully");
      } catch (error) {
        alert("Error withdrawing funds: " + error.message);
      }
    };

    return (
    <div>
      <section>
        <h2>Company Balance</h2>
        <button style={buttonStyle} onClick={getBalance}>Get Balance</button>
        <button style={buttonStyle} onClick={withdraw}>Withdraw All Funds</button>
        {balance !== null && <p>{balance}</p>}
      </section>
      <section>
        <h2>ICP Address</h2>
        <button style={buttonStyle} onClick={getICPAddress}>Get ICP Address</button>
        {address !== null && <p>{address}</p>}
      </section>
    </div>
    );
};

export default BalanceController;
