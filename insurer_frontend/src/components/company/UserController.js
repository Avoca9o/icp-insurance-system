import React, { useState } from "react";
import { fetchApi } from "../../services/Api";
import AddUserButton from "./AddUserButton";
import UpdateUserModal from "./UpdateUserModal";
import buttonStyle from "../../styles/ButtonStyle";

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
        <section>
        <h2>Users</h2>
        <button style={buttonStyle} onClick={fetchUsers}>User List</button>
        <AddUserButton></AddUserButton>
        {users.length > 0 && (
          <ul>
            {users.map((user) => (
              <li key={user.email}>
                {user.email}{" "}
                <button style={buttonStyle} onClick={() => getUser(user.email)}>Open</button>
                <button style={buttonStyle} onClick={() => { setSelectedUser(user.email); setIsModalOpen(true)}}>Update</button>

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
              </li>
            ))}
          </ul>
        )}
        {selectedUser && (
          <div>
            <h3>User Details</h3>
            <p>Email: {selectedUser.email}</p>
            <p>Scheme Version: {selectedUser.scheme_version}</p>
            <p>Insurance Amount: {selectedUser.insurance_amount}</p>

            <button style={buttonStyle} onClick={() => deleteUser(selectedUser.email)}>Delete User</button>
            <button style={buttonStyle} onClick={() => isCheckSumValid(selectedUser.email)}>Check Checksum</button>
          </div>
        )}
      </section>
        </div>
    )
};

export default UserController;
