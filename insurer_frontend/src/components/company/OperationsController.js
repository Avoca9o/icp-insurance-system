import React, { useState } from "react";
import { fetchApi } from "../../services/Api";
import buttonStyle from "../../styles/ButtonStyle";

const OperationsController = () => {
    const [selectedDate, setSelectedDate] = useState("");    
    const [operations, setOperations] = useState([]);

    const token = localStorage.getItem("authToken");

    const fetchOperations = () => {
      if (!selectedDate) {
        return alert("Please select a date");
      }

      fetch(`http://localhost:8001/v1/operations?date=${selectedDate}`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
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
        <h2>Company Operations</h2>
        <div>
          <label>
            Enter date (YYYY-MM-DD):{" "}
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </label>
        </div>
        <button style={buttonStyle} onClick={fetchOperations}>Get Operations</button>
          
        {(
          <div>
            <ul>
              {operations.map((operation, index) => (
                <li key={index}>
                  <p>
                    <strong>User:</strong> {operation.user}
                  </p>
                  <p>
                    <strong>Amount:</strong> {operation.amount}
                  </p>
                  <p>
                    <strong>Date:</strong> {operation.date}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
        </div>
    )
};

export default OperationsController;
