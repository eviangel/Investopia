import React from 'react';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import Dashboard from '../components/Dashboard';
import About from '../components/About';
import Docs from '../components/Docs';
import SignIn from '../components/SignIn';
import { Route, Routes } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <div className="app">
      <Sidebar />
      <Dashboard />
      <div className="main-content">
        {/* <TopBar /> */}
        <div className="content-area">
          <Routes>
            {/* <Route path="/" element={<Dashboard />} /> */}
            <Route path="/about" element={<About />} />
            <Route path="/docs" element={<Docs />} />
            <Route path="/signin" element={<SignIn />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default App;
