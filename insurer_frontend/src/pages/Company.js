import React  from "react";
import BalanceController from "../components/company/BalanceController";
import SchemeController from "../components/company/SchemeController";
import UserController from "../components/company/UserController";
import OperationsController from "../components/company/OperationsController";

const Company = () => {  
    return (
      <div style={{ padding: 20 }}>
        <h1>Интерфейс компании</h1>
        
        <BalanceController></BalanceController>
        
        <SchemeController></SchemeController>

        <UserController></UserController>

        <OperationsController></OperationsController>
    </div>
  );
};
  
export default Company;
