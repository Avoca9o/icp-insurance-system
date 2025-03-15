import React, { useState}  from "react";
import { fetchApi } from "../../services/Api";
import AddUserButton from "./AddUserButton";

const UserController = () => {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);

    const getUser = async (userId) => {
      try {
        const data = await fetchApi(`/v1/user?email=${userId}`, "GET");
        setSelectedUser(data.user);
      } catch (error) {
        alert("Ошибка получения пользователя: " + error.message);
      }
    };

    const deleteUser = async (userId) => {
      if (!window.confirm("Вы уверены, что хотите удалить этого пользователя?")) {
        return;
      }
  
      try {
        await fetchApi(`/v1/user?email=${userId}`, "DELETE");
  
        alert("Пользователь успешно удалён!");
        fetchUsers();
      } catch (error) {
        alert("Ошибка при удалении пользователя: " + error.message);
      }
    };

    const isCheckSumValid = async (userEmail) => {
      try {
        const response = await fetchApi(`/v1/check-sum?email=${userEmail}`, "GET");
  
        if (response['is_valid']) {
          alert("Чек сумма совпадает!");
        } else {
          alert("Чек сумма НЕ совпадает!");
        }
      } catch (error) {
        alert("Ошибка при проверке: " + error.message);
      }
    };

    const fetchUsers = async () => {
      try {
        const data = await fetchApi("/v1/users", "GET");
        setUsers(data.users);
      } catch (error) {
        alert("Ошибка получения списка пользователей: " + error.message);
      }
    };

    return (
        <div>
        <section>
        <h2>Пользователи</h2>
        <button onClick={fetchUsers}>Список пользователей</button>
        <AddUserButton></AddUserButton>
        {users.length > 0 && (
          <ul>
            {users.map((user) => (
              <li>
                {user.email}{" "}
                <button onClick={() => getUser(user.email)}>Открыть</button>
              </li>
            ))}
          </ul>
        )}
        {selectedUser && (
          <div>
            <h3>Детали пользователя</h3>
            <p>Email: {selectedUser.email}</p>
            <p>Версия схемы: {selectedUser.scheme_version}</p>
            <p>Сумма страхования: {selectedUser.insurance_amount}</p>

            <button onClick={() => deleteUser(selectedUser.email)}>Удалить пользователя</button>
            <button onClick={() => isCheckSumValid(selectedUser.email)}>Сверить чек сумму</button>
          </div>
        )}
      </section>
        </div>
    )
};

export default UserController;