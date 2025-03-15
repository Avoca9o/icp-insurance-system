import React, { useState } from "react";
import { fetchApi } from "../../services/Api";

const BalanceController = () => {
    const [balance, setBalance] = useState(null);
    const [address, setAddress] = useState(null);

    const getBalance = async () => {
      try {
        const data = await fetchApi("/v1/balance", "GET");
        setBalance(data.message);
      } catch (error) {
        alert("Ошибка получения баланса: " + error.message);
      }
    };

    const getICPAddress = async () => {
      try {
        const data = await fetchApi("/v1/icp-address", "GET");
        setAddress(data.icp_address);
      } catch (error) {
        alert("Ошибка получения баланса: " + error.message);
      }
    };

    const withdraw = async () => {
      try {
        await fetchApi("/v1/withdraw", "POST");
        alert("Средства успешно выведены");
      } catch (error) {
        alert("Ошибка вывода средств: " + error.message);
      }
    };

    return (
    <div>
    <section>
      <h2>Баланс компании</h2>
      <button onClick={getBalance}>Получить баланс</button>
      <button onClick={withdraw}>Вывести все средства</button>
      {balance !== null && <p>{balance}</p>}
    </section>
    <section>
      <h2>Адрес канистера</h2>
      <button onClick={getICPAddress}>Получить адрес канистера</button>
      {address !== null && <p>{address}</p>}
    </section>
    </div>
    )
};

export default BalanceController