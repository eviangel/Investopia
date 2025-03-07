import React, { useState } from "react";
import PortfolioChart from "./PortfolioChart"; // Contains the two charts
import BubbleChart from "./BubbleChart";         // Contains your additional chart

const DashboardTabs = ({ userId }) => {
  const [activeTab, setActiveTab] = useState("portfolio");

  return (
    <div>
      {/* Tab Navigation */}
      <div className="tabs">
        <button
          className={activeTab === "portfolio" ? "active" : ""}
          onClick={() => setActiveTab("portfolio")}
        >
          Portfolio Charts
        </button>
        <button
          className={activeTab === "third" ? "active" : ""}
          onClick={() => setActiveTab("third")}
        >
          Third Chart
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === "portfolio" && <PortfolioChart userId={userId} />}
        {activeTab === "third" && <BubbleChart userId={userId} />}
      </div>
    </div>
  );
};

export default DashboardTabs;
