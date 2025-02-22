import React, { useState } from "react";
import { register } from "../services/Api"; 

const RegisterForm = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    login: "",
    email: "",
    password: "",
    name: "",
    pay_address: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    try {
      const data = await register(formData);
      console.log("Регистрация успешна:", data);

      setSuccess(true);
      setFormData({
        login: "",
        email: "",
        password: "",
        name: "",
        pay_address: "",
      });
    } catch (err) {
      console.error("Ошибка регистрации:", err);
      setError("Не удалось зарегистрировать компанию. Попробуйте снова.");
    }
  };

  return (
    <form onSubmit={handleRegister}>
      <h2>Регистрация компании</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {success && <p style={{ color: "green" }}>Компания успешно зарегистрирована!</p>}
      <div>
        <label>Логин:</label>
        <input
          type="text"
          name="login"
          value={formData.login}
          onChange={handleChange}
          placeholder="Введите логин"
          required
        />
      </div>
      <div>
        <label>Электронная почта:</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="Введите email"
          required
        />
      </div>
      <div>
        <label>Пароль:</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Введите пароль"
          required
        />
      </div>
      <div>
        <label>Название компании:</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Введите название компании"
          required
        />
      </div>
      <div>
        <label>Адрес выплат (Payout Address):</label>
        <input
          type="text"
          name="pay_address"
          value={formData.pay_address}
          onChange={handleChange}
          placeholder="Введите адрес выплат"
          required
        />
      </div>
      <button type="submit">Зарегистрировать компанию</button>
      <p>
        Уже есть аккаунт?{" "}
        <button type="button" onClick={onSwitchToLogin}>
          Войти
        </button>
      </p>
    </form>
  );
};

export default RegisterForm;