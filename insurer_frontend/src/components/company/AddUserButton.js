import React, { useState } from "react";
import { fetchApi } from "../../services/Api";
import AddUserModal from "./AddUserModal";
import buttonStyle from "../../styles/ButtonStyle";

const AddUserButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false); // Control modal window

  // Adding a user
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
      
      {/* Modal window */}
      {isModalOpen && (
        <AddUserModal
          onClose={() => setIsModalOpen(false)} // Close the modal
          onSubmit={(userData) => {
            addUser(userData); // Call function to send data to the server
          }}
        />
      )}
    </div>
  );
};

export default AddUserButton;

// Styles for the modal window
const modalStyles = {
  position: "fixed",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  backgroundColor: "#fff",
  padding: "20px",
  borderRadius: "8px",
  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
  zIndex: 1000,
};
