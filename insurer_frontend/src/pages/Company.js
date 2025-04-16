import React, { useEffect, useState } from "react";
import BalanceController from "../components/company/BalanceController";
import SchemeController from "../components/company/SchemeController";
import UserController from "../components/company/UserController";
import OperationsController from "../components/company/OperationsController";
import Header from "../styles/Header";
import { fetchApi } from "../services/Api";

const Company = () => {  
    const [companyName, setCompanyName] = useState("");
    const [activeController, setActiveController] = useState("balance");
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    useEffect(() => {
      const getCompanyName = async () => {
        try {
          const data = await fetchApi("/v1/company-name", "GET");
          setCompanyName(data.name);
        } catch (error) {
          console.error("Error fetching company name:", error);
        }
      };

      getCompanyName();
    }, []);

    const toggleMenu = () => {
      setIsMenuOpen(!isMenuOpen);
    };

    const selectController = (controller) => {
      setActiveController(controller);
      setIsMenuOpen(false);
    };

    const renderController = () => {
      switch (activeController) {
        case "balance":
          return <BalanceController />;
        case "scheme":
          return <SchemeController />;
        case "user":
          return <UserController />;
        case "operations":
          return <OperationsController />;
        default:
          return <BalanceController />;
      }
    };

    return (
      <div style={{ padding: 20 }}>
        <Header />
        <h1>Company Interface: {companyName}</h1>
        
        <div className="menu-container" style={{ marginBottom: 20 }}>
          <button 
            className="menu-button" 
            onClick={toggleMenu}
            style={{
              padding: '10px 15px',
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            {activeController.charAt(0).toUpperCase() + activeController.slice(1)} Management
            <span style={{ marginLeft: '10px' }}>{isMenuOpen ? '▼' : '▶'}</span>
          </button>
          
          {isMenuOpen && (
            <div className="dropdown-menu" style={{
              position: 'absolute',
              backgroundColor: '#f9f9f9',
              minWidth: '200px',
              boxShadow: '0px 8px 16px 0px rgba(0,0,0,0.2)',
              zIndex: 1,
              borderRadius: '4px',
              marginTop: '5px'
            }}>
              <div 
                className="menu-item" 
                onClick={() => selectController("balance")}
                style={{
                  padding: '12px 16px',
                  cursor: 'pointer',
                  borderBottom: '1px solid #ddd',
                  backgroundColor: activeController === "balance" ? '#e0e0e0' : 'transparent'
                }}
              >
                Balance Management
              </div>
              <div 
                className="menu-item" 
                onClick={() => selectController("scheme")}
                style={{
                  padding: '12px 16px',
                  cursor: 'pointer',
                  borderBottom: '1px solid #ddd',
                  backgroundColor: activeController === "scheme" ? '#e0e0e0' : 'transparent'
                }}
              >
                Scheme Management
              </div>
              <div 
                className="menu-item" 
                onClick={() => selectController("user")}
                style={{
                  padding: '12px 16px',
                  cursor: 'pointer',
                  borderBottom: '1px solid #ddd',
                  backgroundColor: activeController === "user" ? '#e0e0e0' : 'transparent'
                }}
              >
                User Management
              </div>
              <div 
                className="menu-item" 
                onClick={() => selectController("operations")}
                style={{
                  padding: '12px 16px',
                  cursor: 'pointer',
                  backgroundColor: activeController === "operations" ? '#e0e0e0' : 'transparent'
                }}
              >
                Operations Management
              </div>
            </div>
          )}
        </div>
        
        <div className="controller-container">
          {renderController()}
        </div>
      </div>
    );
};
  
export default Company;
