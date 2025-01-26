import React, { useEffect } from 'react';
import Home from './Home';
import Company from './Company';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

const App = () => {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/company" element={<Company />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;