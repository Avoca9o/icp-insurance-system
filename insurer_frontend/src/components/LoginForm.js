import React, { useState } from "react";
import { logIn } from "../services/Api"; 

const LoginForm = ({ onSwitchToRegister }) => {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const data = await logIn(login, password);
      console.log("Успешный вход:", data);
      if (data.access_token) {
        localStorage.setItem("authToken", data.access_token);
      }

      window.location.href = "/company";
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>Авторизация</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <div>
        <label>Login: </label>
        <input
          type="text"
          placeholder="Введите login"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Пароль: </label>
        <input
          type="password"
          placeholder="Введите пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit">Войти</button>
      <p>
        Нет аккаунта?{" "}
        <button onClick={onSwitchToRegister} type="button">
          Зарегистрироваться
        </button>
      </p>
    </form>
  );
};

export default LoginForm;