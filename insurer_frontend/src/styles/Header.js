import React from 'react';

const Header = () => {
  const headerStyle = {
    backgroundColor: 'lightgreen',
    color: 'maroon',
    textAlign: 'center',
    padding: '10px 0',
    fontSize: '24px'
  };

  return (
    <header style={headerStyle}>
      ICP IMS
    </header>
  );
};

export default Header;