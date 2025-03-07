import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import "./Dashboard.css";
import Notifications from "./Notifications";
import AiRecommendations from "./AiRecommendations";
import News from "./News";
import BalanceInfo from "./BalanceInfo";
import DashboardTabs from "./DashboardTabs";
import Login from "../components/Login";

const Dashboard = () => {
  const navigate = useNavigate();
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    // Get token from localStorage
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/Login"); // Redirect if no token found
      return;
    }

    try {
      const decodedToken = jwtDecode(token);  // ✅ Decode JWT to extract userId
      setUserId(decodedToken.user_id);

      // Check if token is expired
      const currentTime = Date.now() / 1000; // Convert to seconds
      if (decodedToken.exp < currentTime) {
        localStorage.removeItem("token"); // Remove expired token
        localStorage.removeItem("userId");
        navigate("/login"); // Redirect to login
      }
    } catch (error) {
      console.error("Invalid token", error);
      localStorage.removeItem("token"); // Remove invalid token
      localStorage.removeItem("userId");
      navigate("/login"); // Redirect to login
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token"); // ✅ Clear token
    localStorage.removeItem("userId"); // ✅ Clear userId
    navigate("/login"); // ✅ Redirect to login
  };

  return (
    <div className="dashboard">
      <div className="top-section">
        {userId && <BalanceInfo userId={userId} />} {/* ✅ Pass userId */}
      </div>
      <div className="chart-section">
        {userId && <DashboardTabs userId={userId} />}
      </div>
      <div className="main-section">
      {userId && <Notifications userId={userId} />}
      </div>
      <div className="side-section">
        <AiRecommendations />
        <News />
      </div>
    </div>
  );
};

export default Dashboard;
