import React, { useState } from "react";
import { fetchApi } from "../../services/Api";
import { CsvUploader } from "../../services/CsvUploader";
import buttonStyle from "../../styles/ButtonStyle";

const SchemeController = () => {
    const [schemes, setSchemes] = useState([]);
    const [selectedScheme, setSelectedScheme] = useState([]);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [schemeData, setSchemeData] = useState("");

    const fetchSchemes = async () => {
      try {
        const data = await fetchApi("/v1/schemas", "GET");
        setSchemes(data.schemas);
      } catch (error) {
        alert("Error retrieving schemes: " + error.message);
      }
    };

    const addScheme = async () => {
      try {
        // Send scheme data to the server
        await fetchApi("/v1/add-scheme", "POST", { diagnoses_coefs: schemeData });
        alert("Scheme added successfully!");

        // Close the modal and refresh the list of schemes
        setIsModalOpen(false);
        fetchSchemes();

        // Clear the state
        setSchemeData("");
      } catch (error) {
        alert("Error adding scheme: " + error.message);
      }
    };
    
    // Retrieve information on a specific scheme
    const getScheme = async (schemeId) => {
        try {
          const data = await fetchApi(`/v1/schema?global_version_id=${schemeId}`, "GET");
          setSelectedScheme(data.scheme);
        } catch (error) {
          alert("Error retrieving scheme data: " + error.message);
        }
    };

    return (
        <div>
        <section>
          <h2>Schemes</h2>
          <button style={buttonStyle} onClick={fetchSchemes}>List of Schemes</button>
          {schemes.length > 0 && (
            <ul>
              {schemes.map((scheme) => (
                <li key={scheme.id}>
                  Scheme ID: {scheme.id}{" "}
                  <button style={buttonStyle} onClick={() => getScheme(scheme.id)}>Open</button>
                </li>
              ))}
            </ul>
          )}
          <h3>Add New Scheme (CSV)</h3>
          <CsvUploader></CsvUploader>
          <h3>Add New Scheme (JSON)</h3>
          <button style={buttonStyle} onClick={() => setIsModalOpen(true)}>Add Scheme</button>
            {isModalOpen && (
              <div>
                <h3>Add New Scheme (JSON)</h3>
                <br />
                <label>
                  Scheme Data (JSON):
                  <textarea
                    value={schemeData}
                    onChange={(e) => setSchemeData(e.target.value)}
                    placeholder='Enter JSON, e.g., {"CN52": 0.44, "GZ45": 0.5}'
                    rows="5"
                    cols="40"
                  />
                </label>
                <br />
                <button style={buttonStyle} onClick={addScheme}>Submit</button>
                <button style={buttonStyle} onClick={() => setIsModalOpen(false)}>Cancel</button>
              </div>
            )}
          {selectedScheme.length > 0 && (
            <div>
            <h3>Scheme Details</h3>
            {Object.entries(JSON.parse(selectedScheme)).map(([diagnosis, coefficient], index) => (
              <div key={index}>
                <p>
                  <strong>Diagnosis:</strong> {diagnosis}
                </p>
                <p>
                  <strong>Coefficient:</strong> {coefficient}
                </p>
              </div>
            ))}
          </div>
          
          )}
        </section>
        </div>
    )
};

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

export default SchemeController;
