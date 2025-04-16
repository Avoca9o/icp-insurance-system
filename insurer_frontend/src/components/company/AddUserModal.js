import React, { useState } from "react";
import buttonStyle from "../../styles/ButtonStyle";

const AddUserModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    email: "",
    insurance_amount: "",
    schema_version: "",
    secondary_filters: "",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleSubmit = () => {
    try {
      const secondaryFiltersObject = formData.secondary_filters
        ? JSON.parse(formData.secondary_filters)
        : {};

      onSubmit({
        email: formData.email,
        insurance_amount: parseFloat(formData.insurance_amount),
        schema_version: parseInt(formData.schema_version, 10),
        secondary_filters: secondaryFiltersObject,
      });
    } catch (error) {
      alert("JSON format error for secondary filters");
    }
  };

  return (
    <div style={modalStyles}>
      <h3 style={modalTitleStyle}>Add New User</h3>
      <div style={formGroupStyle}>
        <label style={labelStyle}>
          Email:
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            placeholder="Enter email"
            required
            style={inputStyle}
          />
        </label>
      </div>
      
      <div style={formGroupStyle}>
        <label style={labelStyle}>
          Insurance Amount:
          <input
            type="number"
            name="insurance_amount"
            value={formData.insurance_amount}
            onChange={handleInputChange}
            placeholder="Enter amount"
            required
            style={inputStyle}
          />
        </label>
      </div>
      
      <div style={formGroupStyle}>
        <label style={labelStyle}>
          Schema Version:
          <input
            type="number"
            name="schema_version"
            value={formData.schema_version}
            onChange={handleInputChange}
            placeholder="Enter schema version"
            required
            style={inputStyle}
          />
        </label>
      </div>
      
      <div style={formGroupStyle}>
        <label style={labelStyle}>
          Secondary Filters (JSON):
          <textarea
            name="secondary_filters"
            value={formData.secondary_filters}
            onChange={handleInputChange}
            placeholder='Enter JSON, e.g., {"filter1": "value1", "filter2": "value2"}'
            rows="5"
            style={textareaStyle}
          />
        </label>
      </div>
      
      <div style={buttonContainerStyle}>
        <button style={buttonStyle} onClick={handleSubmit}>Submit</button>
        <button style={{...buttonStyle, marginLeft: '10px', backgroundColor: '#f44336'}} onClick={onClose}>Cancel</button>
      </div>
    </div>
  );
};

// Styles for the modal window
const modalStyles = {
  position: "fixed",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  backgroundColor: "#fff",
  padding: "25px",
  borderRadius: "8px",
  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
  zIndex: 1000,
  width: "400px",
  maxWidth: "90%",
};

const modalTitleStyle = {
  marginTop: 0,
  marginBottom: "20px",
  color: "#333",
  borderBottom: "1px solid #eee",
  paddingBottom: "10px",
};

const formGroupStyle = {
  marginBottom: "15px",
};

const labelStyle = {
  display: "block",
  marginBottom: "5px",
  fontWeight: "bold",
  color: "#555",
};

const inputStyle = {
  width: "100%",
  padding: "10px",
  borderRadius: "4px",
  border: "1px solid #ddd",
  fontSize: "14px",
  marginTop: "5px",
};

const textareaStyle = {
  width: "100%",
  padding: "10px",
  borderRadius: "4px",
  border: "1px solid #ddd",
  fontSize: "14px",
  marginTop: "5px",
  resize: "vertical",
};

const buttonContainerStyle = {
  display: "flex",
  justifyContent: "flex-end",
  marginTop: "20px",
};

export default AddUserModal;
