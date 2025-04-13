import React, { useState } from "react";
import { register } from "../services/Api";
import buttonStyle from "../styles/ButtonStyle";

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
      console.log("Registration successful:", data);

      setSuccess(true);
      setFormData({
        login: "",
        email: "",
        password: "",
        name: "",
        pay_address: "",
      });
    } catch (err) {
      console.error("Registration error:", err);
      setError("Failed to register the company. Please try again.");
    }
  };

  return (
    <form onSubmit={handleRegister}>
      <h2>Company Registration</h2>
      {error && <p>{error}</p>}
      {success && <p>Company registered successfully!</p>}
      <div>
        <label>Username:</label>
        <input
          type="text"
          name="login"
          value={formData.login}
          onChange={handleChange}
          placeholder="Enter username"
          required
        />
      </div>
      <div>
        <label>Email:</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="Enter email"
          required
        />
      </div>
      <div>
        <label>Password:</label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Enter password"
          required
        />
      </div>
      <div>
        <label>Company Name:</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Enter company name"
          required
        />
      </div>
      <div>
        <label>Payout Address:</label>
        <input
          type="text"
          name="pay_address"
          value={formData.pay_address}
          onChange={handleChange}
          placeholder="Enter payout address"
          required
        />
      </div>
      <button style={buttonStyle} type="submit">Register Company</button>
      <p>
        Already have an account?{" "}
        <button style={buttonStyle} type="button" onClick={onSwitchToLogin}>
          Log In
        </button>
      </p>
    </form>
  );
};

export default RegisterForm;
