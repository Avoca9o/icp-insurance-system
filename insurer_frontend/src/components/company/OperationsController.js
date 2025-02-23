import React, { useState}  from "react";
import { fetchApi } from "../../services/Api";

const OperationsController = () => {
    const [selectedDate, setSelectedDate] = useState(""); // Состояние для хранения выбранной даты    
    const [operations, setOperations] = useState([]); // Состояние для хранения списка операций

    const fetchOperationsByDate = async () => {
      if (!selectedDate) {
        return alert("Пожалуйста, выберите дату");
      }
    
      try {
        // API-запрос с датой в теле
        const data = await fetchApi(`/v1/operations?date=${selectedDate}`, "GET");
    
        setOperations(data.operations); // Обновить состояние операций
      } catch (error) {
        alert("Ошибка получения операций: " + error.message);
      }
    };

    return (
        <div>
            <section>
        <h2>Операции компании</h2>
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
    )
};

export default OperationsController;