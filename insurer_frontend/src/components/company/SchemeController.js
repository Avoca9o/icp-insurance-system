import React, { useState}  from "react";
import { fetchApi } from "../../services/Api";

const SchemeController = () => {
    const [schemes, setSchemes] = useState([]);
    const [selectedScheme, setSelectedScheme] = useState([]);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [schemeData, setSchemeData] = useState("");


    const fetchSchemes = async () => {
      try {
        const data = await fetchApi("/v1/schemas", "GET");
        setSchemes(data.schemas);
      } catch (error) {
        alert("Ошибка получения схем: " + error.message);
      }
    };

    const addScheme = async () => {
      try {
        // Отправляем данные схемы на сервер
        await fetchApi("/v1/add-scheme", "POST", { diagnoses_coefs: schemeData });
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
    
    // Получение информации по конкретной схеме
    const getScheme = async (schemeId) => {
        try {
          const data = await fetchApi(`/v1/schema?global_version_id=${schemeId}`, "GET");
          setSelectedScheme(data.scheme);
        } catch (error) {
          alert("Ошибка получения данных схемы: " + error.message);
        }
    };


    return (
        <div>
        <section>
          <h2>Схемы</h2>
          <button onClick={fetchSchemes}>Список схем</button>
          <button onClick={() => setIsModalOpen(true)}>Добавить схему</button>
            {isModalOpen && (
              <div style={modalStyles}>
                <h3>Добавить новую схему</h3>
                <br />
                <label>
                  Данные схемы (JSON):
                  <textarea
                    value={schemeData}
                    onChange={(e) => setSchemeData(e.target.value)}
                    placeholder='Введите JSON, например: {"CN52": 0.44, "GZ45": 0.5}'
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
            {Object.entries(JSON.parse(selectedScheme)).map(([diagnosis, coefficient], index) => (
              <div
                key={index}
                style={{
                  marginBottom: "10px",
                  borderBottom: "1px solid #ccc",
                  paddingBottom: "10px",
                }}
              >
                <p>
                  <strong>Диагноз:</strong> {diagnosis}
                </p>
                <p>
                  <strong>Коэффициент:</strong> {coefficient}
                </p>
              </div>
            ))}
          </div>
          
          )}
        </section>
        </div>
    )
};

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

export default SchemeController;