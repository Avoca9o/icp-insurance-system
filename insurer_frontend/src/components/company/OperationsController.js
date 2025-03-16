import React, { useState}  from "react";
import { fetchApi } from "../../services/Api";

const OperationsController = () => {
    const [selectedDate, setSelectedDate] = useState(""); // Состояние для хранения выбранной даты    
    const [operations, setOperations] = useState([]); // Состояние для хранения списка операций

    const token = localStorage.getItem("authToken");

    const fetchOperations = () => {
      if (!selectedDate) {
        return alert("Пожалуйста, выберите дату");
      }

      fetch(`http://localhost:8001/v1/operations?date=${selectedDate}`, {headers: {
        "Authorization": `Bearer ${token}`
      }})
        .then(response => response.blob())
        .then(blob => {
          const url = window.URL.createObjectURL(new Blob([blob]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'data.csv');
          document.body.appendChild(link);
          link.click();
          link.parentNode.removeChild(link);
        })
        .catch(error => console.error('Error downloading the file:', error));
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
        <button onClick={fetchOperations}>Получить операции</button>
          
        {(
          <div style={{ marginTop: "20px" }}>
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
        )
        }
      </section>
        </div>
    )
};

export default OperationsController;