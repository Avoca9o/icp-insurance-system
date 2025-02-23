import React, { useState } from "react";

const AddUserModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    email: "",
    insurance_amount: "",
    schema_version: "",
    secondary_filters: "",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleSubmit = () => {
    try {
      const secondaryFiltersObject = formData.secondary_filters
        ? JSON.parse(formData.secondary_filters)
        : {};

      onSubmit({
        email: formData.email,
        insurance_amount: parseFloat(formData.insurance_amount),
        schema_version: parseInt(formData.schema_version, 10),
        secondary_filters: secondaryFiltersObject,
      });
    } catch (error) {
      alert("Ошибка в формате JSON для вторичных фильтров. Проверьте и повторите попытку.");
    }
  };

  return (
    <div style={modalStyles}>
      <h3>Добавить нового пользователя</h3>
      <label>
        Email:
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleInputChange}
          placeholder="Введите email"
          required
        />
      </label>
      <br />
      <label>
        Страховая сумма:
        <input
          type="number"
          name="insurance_amount"
          value={formData.insurance_amount}
          onChange={handleInputChange}
          placeholder="Введите сумму"
          required
        />
      </label>
      <br />
      <label>
        Версия схемы:
        <input
          type="number"
          name="schema_version"
          value={formData.schema_version}
          onChange={handleInputChange}
          placeholder="Введите версию схемы"
          required
        />
      </label>
      <br />
      <label>
        Вторичные фильтры (JSON):
        <textarea
          name="secondary_filters"
          value={formData.secondary_filters}
          onChange={handleInputChange}
          placeholder='Введите JSON, например: {"filter1": "value1", "filter2": "value2"}'
          rows="5"
          cols="40"
        />
      </label>
      <br />
      <button onClick={handleSubmit}>Отправить</button>
      <button onClick={onClose}>Отмена</button>
    </div>
  );
};

// Стили для модального окна
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

export default AddUserModal;