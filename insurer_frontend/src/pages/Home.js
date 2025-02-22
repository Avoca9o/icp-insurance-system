import React, { useState}  from "react";
import LoginForm from "../components/LoginForm";
import RegisterForm from "../components/RegisterForm";

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