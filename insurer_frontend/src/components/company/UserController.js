import React, { useState } from "react";
import { fetchApi } from "../../services/Api";
import AddUserButton from "./AddUserButton";
import UpdateUserModal from "./UpdateUserModal";
import buttonStyle from "../../styles/ButtonStyle";

// Section container style
const sectionStyle = {
  marginBottom: '30px',
  padding: '15px',
  borderRadius: '8px',
  backgroundColor: '#f9f9f9',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

// List item style
const listItemStyle = {
  padding: '10px',
  marginBottom: '10px',
  backgroundColor: 'white',
  borderRadius: '4px',
  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between'
};

const userDetailStyle = {
  backgroundColor: '#f5f5f5',
  padding: '15px',
  borderRadius: '5px',
  marginBottom: '15px',
};

const UserController = () => {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false); // Control modal window

    const getUser = async (userId) => {
      try {
        const data = await fetchApi(`/v1/user?email=${userId}`, "GET");
        setSelectedUser(data.user);
      } catch (error) {
        alert("Error retrieving user: " + error.message);
      }
    };

    const updateUser = async (userEmail, userData) => {
      try {
        userData["email"] = userEmail;
        await fetchApi(`/v1/update-user`, "POST", userData);
        alert("User updated successfully!");
      } catch (error) {
        alert("Error updating user: " + error.message);
      }
      fetchUsers();
    };

    const deleteUser = async (userId) => {
      if (!window.confirm("Are you sure you want to delete this user?")) {
        return;
      }
  
      try {
        await fetchApi(`/v1/user?email=${userId}`, "DELETE");
  
        alert("User deleted successfully!");
        fetchUsers();
      } catch (error) {
        alert("Error deleting user: " + error.message);
      }
    };

    const isCheckSumValid = async (userEmail) => {
      try {
        const response = await fetchApi(`/v1/check-sum?email=${userEmail}`, "GET");
  
        if (response['is_valid']) {
          alert("Checksum matches!");
        } else {
          alert("Checksum does NOT match!");
        }
      } catch (error) {
        alert("Error checking checksum: " + error.message);
      }
    };

    const fetchUsers = async () => {
      try {
        const data = await fetchApi("/v1/users", "GET");
        setUsers(data.users);
      } catch (error) {
        alert("Error retrieving user list: " + error.message);
      }
    };

    return (
        <div>
        <section style={sectionStyle}>
          <h2>Users</h2>
          <div style={{ marginBottom: '15px', display: 'flex', flexDirection: 'column', gap: '10px', width: '200px' }}>
            <AddUserButton></AddUserButton>
            <button style={{...buttonStyle, width: '100%'}} onClick={fetchUsers}>User List</button>
          </div>
          
          {users.length > 0 && (
            <>
              <ul style={{ listStyleType: 'none', padding: 0 }}>
                {users.map((user) => (
                  <li key={user.email} style={listItemStyle}>
                    <span>{user.email}</span>
                    <div>
                      <button style={buttonStyle} onClick={() => getUser(user.email)}>Open</button>
                      <button style={{...buttonStyle, marginLeft: '5px'}} onClick={() => { setSelectedUser(user.email); setIsModalOpen(true)}}>Update</button>
                      <button style={{...buttonStyle, marginLeft: '5px', backgroundColor: '#f44336'}} onClick={() => deleteUser(user.email)}>Delete</button>
                    </div>
                  </li>
                ))}
              </ul>
              <button style={{...buttonStyle, marginTop: '10px'}} onClick={() => setUsers([])}>Close List</button>
            </>
          )}
        </section>
        
        {selectedUser && (
          <section style={sectionStyle}>
            <h2>User Details</h2>
            <div style={{ marginTop: '15px' }}>
              <div style={userDetailStyle}>
                <p><strong>Email:</strong> {selectedUser.email}</p>
                <p><strong>Scheme Version:</strong> {selectedUser.scheme_version}</p>
                <p><strong>Insurance Amount:</strong> {selectedUser.insurance_amount}</p>
                <p><strong>Secondary Filters:</strong> {selectedUser.secondary_filters ? JSON.stringify(selectedUser.secondary_filters) : 'None'}</p>
                <p><strong>Telegram ID:</strong> {selectedUser.telegram_id || 'Not set'}</p>
                <p><strong>Is Approved:</strong> {selectedUser.is_approved ? 'Yes' : 'No'}</p>
              </div>
              <div style={{ marginTop: '15px' }}>
                <button style={buttonStyle} onClick={() => isCheckSumValid(selectedUser.email)}>Check Sum</button>
                <button style={{...buttonStyle, marginLeft: '10px', backgroundColor: '#f44336'}} onClick={() => setSelectedUser(null)}>Close</button>
              </div>
            </div>
          </section>
        )}
        
        {/* Modal window */}
        {isModalOpen && (
          <UpdateUserModal
            onClose={() => setIsModalOpen(false)} // Close the modal
            onSubmit={(userData) => {
              updateUser(selectedUser, userData); // Call function to send data to the server
              setIsModalOpen(false);
            }}
          />
        )}
        </div>
    )
};

export default UserController;
