import React, { useState } from "react";
import buttonStyle from "../../styles/ButtonStyle";

const UpdateUserModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
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
      <h3>Update User Information</h3>
      <label>
        Insurance Amount:
        <input
          type="number"
          name="insurance_amount"
          value={formData.insurance_amount}
          onChange={handleInputChange}
          placeholder="Enter amount"
          required
        />
      </label>
      <br />
      <label>
        Schema Version:
        <input
          type="number"
          name="schema_version"
          value={formData.schema_version}
          onChange={handleInputChange}
          placeholder="Enter schema version"
          required
        />
      </label>
      <br />
      <label>
        Secondary Filters (JSON):
        <textarea
          name="secondary_filters"
          value={formData.secondary_filters}
          onChange={handleInputChange}
          placeholder='Enter JSON, e.g., {"filter1": "value1", "filter2": "value2"}'
          rows="5"
          cols="40"
        />
      </label>
      <br />
      <button style={buttonStyle} onClick={handleSubmit}>Submit</button>
      <button style={buttonStyle} onClick={onClose}>Cancel</button>
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
  padding: "20px",
  borderRadius: "8px",
  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
  zIndex: 1000,
};

export default UpdateUserModal;
