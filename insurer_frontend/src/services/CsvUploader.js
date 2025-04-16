import React, { useState } from "react";
import buttonStyle from "../styles/ButtonStyle";

export const CsvUploader = () => {
  const [file, setFile] = useState(null);
  const fileInputRef = React.createRef();

  const token = localStorage.getItem("authToken");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert("Please select a file!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://localhost:8001/v1/add-scheme-csv", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`
          },
          body: formData,
        });
        
        const responseData = await response.json();
        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}: ${responseData.message}`);
        }
        alert("File uploaded successfully!");
    } catch (error) {
      alert("Network or server error: " + error.message);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        ref={fileInputRef}
        style={{ display: 'none' }} // скрыть стандартный input
      />
      <button style={buttonStyle} onClick={() => fileInputRef.current.click()}>
        Choose File
      </button>
      <button style={{...buttonStyle, marginLeft: '15px'}} onClick={handleFileUpload}>Upload Scheme</button>
    </div>
  );
}
