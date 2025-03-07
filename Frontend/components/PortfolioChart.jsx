import React, { useEffect, useState } from "react";
import "./PortfolioChart.css"; // Import dedicated CSS for this component
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const PortfolioChart = ({ userId }) => {
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState("All");
  const [selectedYear, setSelectedYear] = useState("All");
  const [years, setYears] = useState([]);
  const [selectedDay, setSelectedDay] = useState(null);
  const [assetFilterMode, setAssetFilterMode] = useState("Exclude Allowed Assets"); // Default option


  // Track visibility of bars for both charts
  const [hiddenBarsFirstChart, setHiddenBarsFirstChart] = useState({
    DEPOSIT_1: false,
    WITHDRAW_1: false,
  });
  const [hiddenBarsSecondChart, setHiddenBarsSecondChart] = useState({
    DEPOSIT_2: false,
    WITHDRAW_2: false,
  });
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/transactions/getuser_deposits_withdraw_${userId}`)
      .then((response) => response.json())
      .then((jsonData) => {
        const allowedAssets = ["USDT", "EUR", "USD","USDC"];

        // Normalize transactions
        const normalizedTransactions = [
          ...jsonData.withdrawals.map(tx => ({ ...tx, action: tx.action.toUpperCase() })), 
          ...jsonData.deposits.map(tx => ({ ...tx, action: tx.action.toUpperCase() }))
        ];

        // Filter transactions to include only allowed assets
        const transactions =
        assetFilterMode === "Exclude Allowed Assets"
          ? normalizedTransactions.filter(tx => !allowedAssets.includes(tx.asset)) // Exclude USDT, EUR, USD
          : normalizedTransactions.filter(tx => allowedAssets.includes(tx.asset));  // Include ONLY USDT, EUR, USD

        const aggregatedDaily = {};
        const extractedYears = new Set();
        const availableAssets = new Set();

        transactions.forEach((transaction) => {
          const date = new Date(transaction.time).toISOString().split("T")[0];
          const year = date.split("-")[0];
          extractedYears.add(year);
          availableAssets.add(transaction.asset);

          if (!aggregatedDaily[date]) {
            aggregatedDaily[date] = {
              date,
              transactions: [],
              assetList: [],
              DEPOSIT_1: 0,
              WITHDRAW_1: 0,
            };
          }

          aggregatedDaily[date].transactions.push(transaction);
          aggregatedDaily[date].assetList.push(transaction.asset);
          

          if (transaction.action === "DEPOSIT") {
            aggregatedDaily[date].DEPOSIT_1 += parseFloat(transaction.quantity);
          } else if (transaction.action === "WITHDRAW") {
            aggregatedDaily[date].WITHDRAW_1 += parseFloat(transaction.quantity);
          }
        });

        const sortedDailyData = Object.values(aggregatedDaily).sort(
          (a, b) => new Date(a.date) - new Date(b.date)
        );

        const summaryData = {};
        transactions.forEach((transaction) => {
          const key = transaction.asset;
          if (!summaryData[key]) {
            summaryData[key] = {
              asset: transaction.asset,
              DEPOSIT_2: 0,
              WITHDRAW_2: 0,
            };
          }
          if (transaction.action === "DEPOSIT") {
            summaryData[key].DEPOSIT_2 += parseFloat(transaction.quantity);
          } else if (transaction.action === "WITHDRAW") {
            summaryData[key].WITHDRAW_2 += parseFloat(transaction.quantity);
          }
        });

        // Filter out data points where both deposit and withdrawal are zero
        const nonZeroFilteredData = sortedDailyData.filter(item => item.DEPOSIT_1 > 0 || item.WITHDRAW_1 > 0);
        const nonZeroSummaryData = Object.values(summaryData).filter(item => item.DEPOSIT_2 > 0 || item.WITHDRAW_2 > 0);

        setData(nonZeroFilteredData);
        setFilteredData(nonZeroFilteredData);
        setSummary(nonZeroSummaryData);
        setYears(["All", ...Array.from(extractedYears).sort()]);
      
        if (!availableAssets.has(selectedAsset)) {
          setSelectedAsset("All");
        }
      })

      .catch((error) => console.error("Error fetching data:", error));
}, [userId,assetFilterMode]);

  // Filtering for asset and year
  useEffect(() => {
      let filtered = [...data];

      if (selectedAsset !== "All") {
          filtered = filtered
              .map((item) => {
                  // Filter transactions to keep only selected asset
                  const filteredTransactions = item.transactions.filter(tx => tx.asset === selectedAsset);

                  // If no transactions remain for the selected asset, remove the date entry
                  if (filteredTransactions.length === 0) return null;

                  // Recalculate deposit and withdrawal values
                  const depositTotal = filteredTransactions
                      .filter(tx => tx.action === "DEPOSIT")
                      .reduce((sum, tx) => sum + parseFloat(tx.quantity), 0);

                  const withdrawTotal = filteredTransactions
                      .filter(tx => tx.action === "WITHDRAW")
                      .reduce((sum, tx) => sum + parseFloat(tx.quantity), 0);

                  return {
                      ...item,
                      transactions: filteredTransactions,
                      assetList: [selectedAsset], // Ensure only the selected asset remains
                      DEPOSIT_1: depositTotal,
                      WITHDRAW_1: withdrawTotal
                  };
              })
              .filter(item => item !== null); // Remove empty days
      }

      if (selectedYear !== "All") {
          filtered = filtered.filter((item) => item.date.startsWith(selectedYear));
      }

      setFilteredData(filtered);
  }, [selectedAsset, selectedYear, data]);

  // Legend click handlers
  const handleLegendClickFirstChart = (event) => {
    setHiddenBarsFirstChart((prev) => ({
      ...prev,
      [event.dataKey]: !prev[event.dataKey],
    }));
  };

  const handleLegendClickSecondChart = (event) => {
    setHiddenBarsSecondChart((prev) => ({
      ...prev,
      [event.dataKey]: !prev[event.dataKey],
    }));
  };

  // Custom Legend Renderer
  const renderCustomLegend = (hiddenBars, handleLegendClick) => (props) => {
    const { payload } = props;
    return (
      <div style={{ display: "flex", justifyContent: "center", gap: "20px", cursor: "pointer" }}>
        {payload.map((entry) => (
          <span
            key={entry.value}
            onClick={() => handleLegendClick(entry)}
            style={{
              textDecoration: hiddenBars[entry.dataKey] ? "line-through" : "none",
              color: entry.color,
              fontWeight: "bold",
              cursor: "pointer",
              transition: "opacity 0.3s ease",
              opacity: hiddenBars[entry.dataKey] ? 0.5 : 1,
            }}
          >
            {entry.value}
          </span>
        ))}
      </div>
    );
  };

  // Custom Tooltip for the main charts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const isFirstChart = payload[0]?.payload?.date;
      const assetName = isFirstChart
        ? payload[0]?.payload?.assetList?.join(", ") || "Unknown"
        : payload[0]?.payload?.asset || "Unknown";
      // Function to format large numbers
      const formatValue = (value) => (value >= 10000 ? `${value / 1000} * 10³` : value);
      return (
        <div
          style={{
            background: "#fff",
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "5px",
            boxShadow: "2px 2px 10px rgba(0, 0, 0, 0.2)",
          }}
        >
          {isFirstChart && <p style={{ color: "#333", fontWeight: "bold" }}>Date: {label}</p>}
          <p style={{ color: "#3498db", fontWeight: "bold" }}>Asset(s): {assetName}</p>
          <p style={{ color: "#2ecc71", fontWeight: "bold" }}>Deposits: {payload[0].value}</p>
          <p style={{ color: "#e74c3c", fontWeight: "bold" }}>Withdrawals: {payload[1]?.value || 0}</p>
        </div>
      );
    }
    return null;
  };

  // Custom Tooltip for the popup chart
  const PopupCustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const transaction = payload[0].payload;
      return (
        <div
          style={{
            background: "#fff",
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "5px",
            boxShadow: "2px 2px 10px rgba(0, 0, 0, 0.2)",
          }}
        >
          <p style={{ fontWeight: "bold", marginBottom: "5px" }}>Time: {label}</p>
          <p style={{ color: "#3498db", fontWeight: "bold", marginBottom: "5px" }}>
            Asset: {transaction.asset || "Unknown"}
          </p>
          <p style={{ color: "#2ecc71", fontWeight: "bold", marginBottom: "5px" }}>
            Deposit: {transaction.deposit}
          </p>
          <p style={{ color: "#e74c3c", fontWeight: "bold" }}>
            Withdrawal: {transaction.withdrawal}
          </p>
        </div>
      );
    }
    return null;
  };

  // Safe-checked click handler for bars in the first chart
  const handleBarClick = (data, index) => {
    if (!data || !data.payload || !data.payload.transactions) {
      console.warn("handleBarClick: data or data.payload.transactions is undefined", data);
      return;
    }
    setSelectedDay(data.payload);
  };

  return (
    <div>
      <h3>Daily Deposits & Withdrawals</h3>

      {/* Filters Row */}
      <div className="filter-row">
        <div className="filter-item">
          <label>Filter Assets: </label>
          <select
            value={assetFilterMode}
            onChange={(e) => setAssetFilterMode(e.target.value)}
          >
            <option value="Exclude Allowed Assets">Crypto</option>
            <option value="Include Allowed Assets">Fiat</option>
          </select>
        </div>
        <div className="filter-item">
          <label>Select Asset: </label>
          <select
            value={selectedAsset}
            onChange={(e) => setSelectedAsset(e.target.value)}
          >
            <option value="All">All</option>
            {summary.map((s) => (
              <option key={s.asset} value={s.asset}>
                {s.asset}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-item">
          <label>Select Year: </label>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
      </div>
    
      {/* Main Chart */}
      <ResponsiveContainer width="100%" height={400} style={{ marginBottom: "50px" }}>
        <BarChart data={filteredData}>
          <CartesianGrid strokeDasharray="0.1 0.1" />
          <XAxis dataKey="date" />
          <YAxis scale="log" domain={[0.0001, "auto"]} allowDataOverflow />
          <Tooltip content={<CustomTooltip />} />
          <Legend content={renderCustomLegend(hiddenBarsFirstChart, handleLegendClickFirstChart)} />
          <Bar
            dataKey="DEPOSIT_1"
            fill="#82ca9d"
            name="Deposits"
            hide={hiddenBarsFirstChart.DEPOSIT_1}
            onClick={handleBarClick}
            minPointSize={10}
          />
          <Bar
            dataKey="WITHDRAW_1"
            fill="#ff6666"
            name="Withdrawals"
            hide={hiddenBarsFirstChart.WITHDRAW_1}
            onClick={handleBarClick}
            minPointSize={10}
          />
        </BarChart>
      </ResponsiveContainer>

      <h3>Accumulated Deposits & Withdrawals by Asset</h3>

      {/* Second Chart (Summary) */}
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={summary}>
          <CartesianGrid strokeDasharray="0.1 0.1" />
          <XAxis dataKey="asset" />
          <YAxis scale="log" domain={[0.0001, "auto"]} allowDataOverflow />
          <Tooltip content={<CustomTooltip />} />
          <Legend content={renderCustomLegend(hiddenBarsSecondChart, handleLegendClickSecondChart)} />
          <Bar
            dataKey="DEPOSIT_2"
            fill="#82ca9d"
            name="Total Deposits"
            hide={hiddenBarsSecondChart.DEPOSIT_2}
          />
          <Bar
            dataKey="WITHDRAW_2"
            fill="#ff6666"
            name="Total Withdrawals"
            hide={hiddenBarsSecondChart.WITHDRAW_2}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Popup Modal for the Selected Day */}
      {selectedDay && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button
              style={{ position: "absolute", top: 10, right: 10 }}
              onClick={() => setSelectedDay(null)}
            >
              Close
            </button>
            <h4>Transactions for {selectedDay.date}</h4>
            {selectedDay.transactions && selectedDay.transactions.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={selectedDay.transactions.map((t) => ({
                    ...t,
                    timeLabel: new Date(t.time).toLocaleTimeString(),
                    deposit: t.action === "DEPOSIT" ? parseFloat(t.quantity) : 0,
                    withdrawal: t.action === "WITHDRAW" ? parseFloat(t.quantity) : 0,
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  {/* Use CSS classes for popup chart axis styling */}
                  <XAxis dataKey="timeLabel" className="popup-xaxis" />
                  <YAxis className="popup-yaxis" />
                  <Tooltip content={<PopupCustomTooltip />} />
                  <Legend />
                  <Bar dataKey="deposit" fill="#82ca9d" name="Deposit" />
                  <Bar dataKey="withdrawal" fill="#ff6666" name="Withdrawal" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p>No transactions found for this day.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioChart;
