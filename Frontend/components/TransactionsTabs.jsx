import React, { useState } from "react";
import TransactionsChart from "./TransactionsChart";
import ThirdChart from "./BubbleChart"; // Your new chart component

const TransactionsTabs = () => {
  const [activeTab, setActiveTab] = useState("transactions");

  return (
    <div>
      {/* Tab Navigation */}
      <div className="tabs">
        <button
          className={activeTab === "transactions" ? "active" : ""}
          onClick={() => setActiveTab("transactions")}
        >
          Transactions Chart
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
        {activeTab === "transactions" && <TransactionsChart />}
        {activeTab === "third" && <ThirdChart />}
      </div>
    </div>
  );
};

export default TransactionsTabs;
