import React, { useState}  from "react";
import { fetchApi } from "./api";
import AddUserButton from "./AddUserButton";

const Company = () => {
    const [balance, setBalance] = useState(null);
    const [address, setAddress] = useState(null);
    const [schemes, setSchemes] = useState([]);
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [selectedScheme, setSelectedScheme] = useState([]);
    const [selectedDate, setSelectedDate] = useState(""); // Состояние для хранения выбранной даты    
    const [operations, setOperations] = useState([]); // Состояние для хранения списка операций

    const [isModalOpen, setIsModalOpen] = useState(false); // Управление модальным окном
    const [schemeData, setSchemeData] = useState(""); // Данные схемы в виде JSON

  
    // Получение баланса компании
    const getBalance = async () => {
      try {
        const data = await fetchApi("/v1/get-balance", "GET");
        setBalance(data.message);
      } catch (error) {
        alert("Ошибка получения баланса: " + error.message);
      }
    };

    // Получение адреса кошелька канистера
    const getICPAddress = async () => {
        try {
          const data = await fetchApi("/v1/get-icp-address", "GET");
          setAddress(data.icp_address);
        } catch (error) {
          alert("Ошибка получения баланса: " + error.message);
        }
      };
  
    // Добавление схемы
    const addScheme = async () => {
      try {
        // Парсинг данных схемы (JSON)
        const parsedData = JSON.parse(schemeData);

        // Отправляем данные схемы на сервер
        await fetchApi("/v1/add-scheme", "POST", { diagnoses_coefs: parsedData });
        alert("Схема добавлена успешно!");

        // Закрываем модальное окно и обновляем список схем
        setIsModalOpen(false);
        fetchSchemes();

        // Очищаем состояние
        setSchemeData("");
      } catch (error) {
        alert("Ошибка добавления схемы: " + error.message);
      }
    };
    
  
    // Получение списка схем
    const fetchSchemes = async () => {
      try {
        const data = await fetchApi("/v1/get-schemas", "GET");
        setSchemes(data.schemas);
      } catch (error) {
        alert("Ошибка получения схем: " + error.message);
      }
    };
  
    // Получение информации по конкретной схеме
    const getScheme = async (schemeId) => {
        try {
          const data = await fetchApi(`/v1/get-schema?global_version_id=${schemeId}`, "GET");
          setSelectedScheme(data.scheme); // Ожидается, что API вернет детализированный объект схемы
        } catch (error) {
          alert("Ошибка получения данных схемы: " + error.message);
        }
    };
  
    // Получение списка пользователей
    const fetchUsers = async () => {
      try {
        const data = await fetchApi("/v1/get-users", "GET");
        setUsers(data.users);
      } catch (error) {
        alert("Ошибка получения списка пользователей: " + error.message);
      }
    };
  
    // Получение информации о конкретном пользователе
    const getUser = async (userId) => {
      try {
        const data = await fetchApi(`/v1/get-user?email=${userId}`, "GET");
        setSelectedUser(data.user);
      } catch (error) {
        alert("Ошибка получения пользователя: " + error.message);
      }
    };

    const fetchOperationsByDate = async () => {
      if (!selectedDate) {
        return alert("Пожалуйста, выберите дату");
      }
    
      try {
        // API-запрос с датой в теле
        const data = await fetchApi(`/v1/get-operations?date=${selectedDate}`, "GET");
    
        setOperations(data.operations); // Обновить состояние операций
      } catch (error) {
        alert("Ошибка получения операций: " + error.message);
      }
    };

    const deleteUser = async (userId) => {
      if (!window.confirm("Вы уверены, что хотите удалить этого пользователя?")) {
        return;
      }

      try {
        await fetchApi(`/v1/delete-user?email=${userId}`, "DELETE");

        alert("Пользователь успешно удалён!");
        fetchUsers(); // Обновляем список пользователей после удаления
      } catch (error) {
        alert("Ошибка при удалении пользователя: " + error.message);
      }
    };
  
    return (
      <div style={{ padding: 20 }}>
        <h1>Интерфейс компании</h1>
        
        {/* Баланс компании */}
        <section>
          <h2>Баланс компании</h2>
          <button onClick={getBalance}>Получить баланс</button>
          {balance !== null && <p>{balance}</p>}
        </section>
        <section>
          <h2>Адрес канистера</h2>
          <button onClick={getICPAddress}>Получить адрес канистера</button>
          {address !== null && <p>{address}</p>}
        </section>
        
        {/* Управление схемами */}
        <section>
          <h2>Схемы</h2>
          <button onClick={fetchSchemes}>Список схем</button>
          <button onClick={() => setIsModalOpen(true)}>Добавить схему</button>
          {/* Модальное окно */}
            {isModalOpen && (
              <div style={modalStyles}>
                <h3>Добавить новую схему</h3>
                <br />
                <label>
                  Данные схемы (JSON):
                  <textarea
                    value={schemeData}
                    onChange={(e) => setSchemeData(e.target.value)}
                    placeholder='Введите JSON, например: [{"diagnoses": "SF432.2", "coef": 0.5}]'
                    rows="5"
                    cols="40"
                  />
                </label>
                <br />
                <button onClick={addScheme}>Отправить</button>
                <button onClick={() => setIsModalOpen(false)}>Отмена</button>
              </div>
            )}
          {schemes.length > 0 && (
            <ul>
              {schemes.map((scheme) => (
                <li key={scheme.id}>
                  Схема ID: {scheme.id}{" "}
                  <button onClick={() => getScheme(scheme.id)}>Открыть</button>
                </li>
              ))}
            </ul>
          )}
          {selectedScheme.length > 0 && (
            <div>
              <h3>Детали схемы</h3>
              {selectedScheme.map((item, index) => (
                <div
                  key={index}
                  style={{
                    marginBottom: "10px",
                    borderBottom: "1px solid #ccc",
                    paddingBottom: "10px",
                  }}
                >
                  <p>
                    <strong>Диагноз:</strong> {item.diagnoses}
                  </p>
                  <p>
                    <strong>Коэффициент:</strong> {item.coef}
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>

      {/* Управление пользователями */}
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

            {/* Кнопка Удаления */}
            <button onClick={() => deleteUser(selectedUser.email)}>Удалить пользователя</button>
          </div>
        )}
      </section>

      <section>
        <h2>Операции компании</h2>
        {/* Поле ввода для даты */}
        <div style={{ marginBottom: "10px" }}>
          <label>
            Введите дату (YYYY-MM-DD):{" "}
            <input
              type="date"
              value={selectedDate} // состояние для хранения введенной даты
              onChange={(e) => setSelectedDate(e.target.value)} // обновление состояния при изменении
            />
          </label>
        </div>
        <button onClick={fetchOperationsByDate}>Получить операции</button>
          
        {/* Отображение операций компании */}
        {operations.length > 0 ? (
          <div style={{ marginTop: "20px" }}>
            <h3>Операции за {selectedDate}</h3>
            <ul>
              {operations.map((operation, index) => (
                <li key={index} style={{ marginBottom: "10px" }}>
                  <p>
                    <strong>Пользователь:</strong> {operation.user}
                  </p>
                  <p>
                    <strong>Сумма:</strong> {operation.amount}
                  </p>
                  <p>
                    <strong>Дата:</strong> {operation.date}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          selectedDate && (
            <p>Нет доступных операций для даты {selectedDate}.</p>
          )
        )}
      </section>
    </div>
  );
};
  
export default Company;

// Стили для простого модального окна
const modalStyles = {
    position: "fixed",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "8px",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    zIndex: 1000,
  };