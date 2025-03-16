export const getToken = () => {
  return localStorage.getItem("authToken");
};

export const fetchApi = async (url, method = "GET", body = null) => {
  const token = getToken();

  if (!token) {
    throw new Error("Необходимо авторизоваться");
  }

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  const options = {
    method,
    headers,
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`http://localhost:8001${url}`, options);
  const responseData = await response.json();

  if (!response.ok) {
    throw new Error(`Ошибка: ${response.statusText}: ${responseData.message}`);
  }

  return responseData;
};

export const logIn = async (login, password) => {
  const response = await fetch("http://localhost:8001/v1/authorize", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ login, password }),
  });

  if (!response.ok) {
    throw new Error((await response.json()).message || "Ошибка при авторизации");
  }

  return response.json();
};

export const register = async (formData) => {
  const response = await fetch("http://127.0.0.1:8001/v1/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    throw new Error("Ошибка регистрации: " + response.statusText);
  }

  return response.json();
};
