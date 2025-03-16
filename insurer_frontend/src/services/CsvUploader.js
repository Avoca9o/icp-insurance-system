import React, { useState } from "react";

export const CsvUploader = () => {
  const [file, setFile] = useState(null);

  const token = localStorage.getItem("authToken");

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert("Выберите файл!");
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
          throw new Error(`Ошибка: ${response.statusText}: ${responseData.message}`);
        }
        alert("Файл успешно добавлен!")
    } catch (error) {
      alert("Ошибка сети или сервера: " + error.message);
    }
  };

  return (
    <div>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={handleFileUpload}>Добавить схему</button>
    </div>
  );
}
