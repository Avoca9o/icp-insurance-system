import React, { useState } from "react";
import { logIn } from "../services/Api"; 
import buttonStyle from "../styles/ButtonStyle";


const LoginForm = ({ onSwitchToRegister }) => {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const data = await logIn(login, password);
      console.log("Login successful:", data);
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
      <h2>Login</h2>
      {error && <p>{error}</p>}
      <div>
        <label>Username: </label>
        <input
          type="text"
          placeholder="Enter username"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Password: </label>
        <input
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button style={buttonStyle} type="submit">Log In</button>
      <p>
        Don't have an account?{" "}
        <button onClick={onSwitchToRegister} style={buttonStyle} type="button">
          Register
        </button>
      </p>
    </form>
  );
};

export default LoginForm;