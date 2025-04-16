import React, { useState } from "react";
import { fetchApi } from "../../services/Api";
import AddUserModal from "./AddUserModal";
import buttonStyle from "../../styles/ButtonStyle";

const AddUserButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const addUser = async (userData) => {
    try {
      await fetchApi("/v1/add-user", "POST", userData);
      alert("User added successfully!");
    } catch (error) {
      alert("Error adding user: " + error.message);
    }
  };

  return (
    <div style={{ width: '100%' }}>
      <button style={{...buttonStyle, width: '100%'}} onClick={() => setIsModalOpen(true)}>Add User</button>
      
      {}
      {isModalOpen && (
        <AddUserModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={(userData) => {
            addUser(userData);
          }}
        />
      )}
    </div>
  );
};

export default AddUserButton;
