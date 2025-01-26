// Получение токена из localStorage
export const getToken = () => {
  return localStorage.getItem("authToken");
};

// Универсальная функция для работы с API запросами
export const fetchApi = async (url, method = "GET", body = null) => {
  const token = getToken(); // Достаем токен из localStorage

  if (!token) {
    throw new Error("Необходимо авторизоваться");
  }

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`, // Передаем токен
  };

  const options = {
    method,
    headers,
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`http://localhost:8000${url}`, options);

  // Проверим статус ответа
  if (!response.ok) {
    throw new Error(`Ошибка: ${response.statusText}`);
  }

  return await response.json();
};