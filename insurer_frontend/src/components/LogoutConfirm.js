import React from 'react';

const LogoutConfirm = ({ onConfirm, onCancel }) => {
  return (
    <div className="logout-confirmation" style={{
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      backgroundColor: 'white',
      padding: '20px',
      borderRadius: '8px',
      boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
      zIndex: 1000,
      width: '300px',
      textAlign: 'center'
    }}>
      <h3 style={{ marginTop: 0 }}>Confirm Logout</h3>
      <p>Are you sure you want to log out?</p>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '20px' }}>
        <button 
          onClick={onConfirm}
          style={{
            padding: '8px 16px',
            backgroundColor: '#f44336',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Yes
        </button>
        <button 
          onClick={onCancel}
          style={{
            padding: '8px 16px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          No
        </button>
      </div>
    </div>
  );
};

export default LogoutConfirm; 