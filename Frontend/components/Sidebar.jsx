import React from 'react';
import './Sidebar.css';
import { FaChartBar, FaChartLine, FaUser, FaBell, FaHeadset, FaCogs, FaSignOutAlt } from 'react-icons/fa';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h2 className="sidebar-title">Cryptocoin</h2>
      <ul className="sidebar-menu">
        <li className="sidebar-item"><FaChartBar className="sidebar-icon" /> <span className="sidebar-text">Dashboard</span></li>
        <li className="sidebar-item"><FaChartLine className="sidebar-icon" /> <span className="sidebar-text">Trade History</span></li>
        <li className="sidebar-item"><FaUser className="sidebar-icon" /> <span className="sidebar-text">Profile</span></li>
        <li className="sidebar-item"><FaBell className="sidebar-icon" /> <span className="sidebar-text">Notifications</span></li>
      </ul>
      <div className="sidebar-footer">
        <p><FaHeadset className="sidebar-icon" /> <span className="sidebar-text">Support</span></p>
        <p><FaCogs className="sidebar-icon" /> <span className="sidebar-text">Settings</span></p>
        <p><FaSignOutAlt className="sidebar-icon" /> <span className="sidebar-text">Log out</span></p>
      </div>
    </div>
  );
};

export default Sidebar;


