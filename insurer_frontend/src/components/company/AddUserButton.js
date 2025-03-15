import React, { useState } from "react";
import { fetchApi } from "../../services/Api";
import AddUserModal from "./AddUserModal";

const AddUserButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // Управление модальным окном

  // Добавление пользователя
  const addUser = async (userData) => {
    try {
      await fetchApi("/v1/add-user", "POST", userData);
      alert("Пользователь добавлен успешно!");
      
    } catch (error) {
      alert("Ошибка добавления пользователя: " + error.message);
    }
  };

  return (
    <div>
      <button onClick={() => setIsModalOpen(true)}>Добавить пользователя</button>
      
      {/* Модальное окно */}
      {isModalOpen && (
        <AddUserModal
          onClose={() => setIsModalOpen(false)} // Закрываем окно
          onSubmit={(userData) => {
            addUser(userData); // Вызываем функцию для отправки данных на сервер
          }}
        />
      )}
    </div>
  );
};

export default AddUserButton;

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