import React, { useEffect } from 'react';
import Home from './pages/Home';
import Company from './pages/Company';
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