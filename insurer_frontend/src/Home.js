import React, { useState}  from "react";

// Форма авторизации
const LoginForm = ({ onSwitchToRegister }) => {
  // Состояния для хранения данных формы
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(""); // Сбрасываем ошибку перед новой попыткой

    try {
      // Запрос на сервер
      const response = await fetch("http://localhost:8000/v1/authorize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ login, password }),
      });

      // Проверяем успешность запроса
      if (!response.ok) {
        throw new Error(response.json());
      }

      // Обработка успешного результата
      const data = await response.json();
      console.log("Успешный вход:", data);

      // Сохранение токена в локальное хранилище, если он передается сервером
      if (data.access_token) {
        localStorage.setItem("authToken", data.access_token);
      }

      window.location.href = "/company"; // Пример перенаправления
    } catch (err) {
      console.error(err);
      setError(err.message); // Отображаем ошибку
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>Авторизация</h2>

      {/* Отображение сообщения об ошибке */}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div>
        <label>Login: </label>
        <input
          type="login"
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

// Форма регистрации
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

  // Обработчик изменения полей формы
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  // Обработчик отправки формы
  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    try {
      const response = await fetch("http://127.0.0.1:8000/v1/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Ошибка регистрации: " + response.statusText);
      }

      const data = await response.json();
      console.log("Регистрация успешна:", data);
      setSuccess(true);

      // Очистка формы
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
  

const Home = () => {
    const [isLogin, setIsLogin] = useState(true);

    return (
      <div style={{ maxWidth: "400px", margin: "auto", padding: "20px", textAlign: "center", border: "1px solid #ccc", borderRadius: "8px", boxShadow: "0 4px 8px rgba(0,0,0,0.1)" }}>
        {isLogin ? (
          <LoginForm onSwitchToRegister={() => setIsLogin(false)} />
        ) : (
          <RegisterForm onSwitchToLogin={() => setIsLogin(true)} />
        )}
      </div>
    );
};
  
export default Home;