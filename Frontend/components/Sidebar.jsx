import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from "../src/utils/UserContext";
import './Sidebar.css';
import {
  FaChartBar,
  FaChartLine,
  FaUser,
  FaBell,
  FaHeadset,
  FaCogs,
  FaSignOutAlt,
  FaDatabase
} from 'react-icons/fa';

// A reusable component for each sidebar item
const SidebarItem = ({ icon, label, path, onClick }) => {
  const navigate = useNavigate();

  // If onClick is provided, use it; otherwise navigate using the path if available
  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (path) {
      navigate(path);
    }
  };

  return (
    <li className="sidebar-item" onClick={handleClick}>
      <span className="sidebar-icon">{icon}</span>
      <span className="sidebar-text">{label}</span>
    </li>
  );
};

const Sidebar = () => {

  const navigate = useNavigate();
  const { setUserId } = useUser(); // Extract setUserId from context
  const handleLogout = () => {
    // Clear token and userId from local storage
    localStorage.removeItem("token");
    localStorage.removeItem("userId");

    // Clear userId from context (if using context)
    setUserId(null);

    // Navigate to the login page
    navigate("/login");
  };

  // Define the main menu items. Each item can include a path or onClick handler.
  const menuItems = [
    { label: 'Dashboard', icon: <FaChartBar />, path: '/' },
    { label: 'Trade History', icon: <FaChartLine />, path: '/trade-history' },
    { label: 'Profile', icon: <FaUser />, path: '/profile' },
    { label: 'Notifications', icon: <FaBell />, path: '/notifications' },
    { label: 'Daily Performance', icon: <FaDatabase />, path: '/dailyperformance' },
  ];

  // Define footer items separately; you can also assign an onClick function if needed.
  const footerItems = [
    { label: 'Support', icon: <FaHeadset />, path: '/support' },
    { label: 'Settings', icon: <FaCogs />, path: '/settings' },
    // { label: 'Log out', icon: <FaSignOutAlt />, onClick: handleLogout },
  ];

  return (
    <div className="sidebar">
      <h2 className="sidebar-title">Cryptocoin</h2>
      <ul className="sidebar-menu">
        {menuItems.map((item, idx) => (
          <SidebarItem key={idx} {...item} />
        ))}
      </ul>
      <div className="sidebar-footer">
        {footerItems.map((item, idx) => (
          <p key={idx} onClick={() => item.onClick ? item.onClick() : navigate(item.path)} className="sidebar-footer-item">
            <span className="sidebar-icon">{item.icon}</span>
            <span className="sidebar-text">{item.label}</span>
          </p>
        ))}
        <button onClick={handleLogout} className="logout-button">
          <span className="sidebar-icon"><FaSignOutAlt /></span>
          <span className="sidebar-text">Log out</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
