import React, { useState } from "react";
import buttonStyle from "../../styles/ButtonStyle";

const sectionStyle = {
  marginBottom: '30px',
  padding: '15px',
  borderRadius: '8px',
  backgroundColor: '#f9f9f9',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

const OperationsController = () => {
    const [selectedDate, setSelectedDate] = useState("");    
    const [operations, setOperations] = useState([]);

    const token = localStorage.getItem("authToken");

    const fetchOperations = () => {
      if (!selectedDate) {
        return alert("Please select a date");
      }

      fetch(`http://84.252.131.59:8001/v1/operations?date=${selectedDate}`, {
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
            <section style={sectionStyle}>
              <h2>Company Operations</h2>
              <div style={{ marginBottom: '15px' }}>
                <label>
                  Enter date (YYYY-MM-DD):{" "}
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </label>
              </div>
              <button style={buttonStyle} onClick={fetchOperations}>Get Operations</button>
              
              {operations.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                  <h3>Operations List</h3>
                  <ul style={{ listStyleType: 'none', padding: 0 }}>
                    {operations.map((operation, index) => (
                      <li key={index} style={{ 
                        padding: '10px', 
                        marginBottom: '10px', 
                        backgroundColor: 'white', 
                        borderRadius: '4px',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                      }}>
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
