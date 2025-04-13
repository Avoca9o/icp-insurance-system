import React, { useEffect, useState } from "react";
import BalanceController from "../components/company/BalanceController";
import SchemeController from "../components/company/SchemeController";
import UserController from "../components/company/UserController";
import OperationsController from "../components/company/OperationsController";
import Header from "../styles/Header";
import { fetchApi } from "../services/Api";

const Company = () => {  
    const [companyName, setCompanyName] = useState("");

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

    return (
      <div style={{ padding: 20 }}>
        <Header />
        <h1>Company Interface: {companyName}</h1>
        
        <BalanceController></BalanceController>
        
        <SchemeController></SchemeController>

        <UserController></UserController>

        <OperationsController></OperationsController>
    </div>
  );
};
  
export default Company;
