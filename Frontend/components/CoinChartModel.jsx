import React, { useState, useEffect } from "react";
import "./CoinChartModel.css";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const CoinChartModel = ({ coinSymbol, onClose }) => {
  const [chartData, setChartData] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [days, setDays] = useState(7);
  const [percentageChange, setPercentageChange] = useState(0); // <-- NEW

  if (!coinSymbol) return null;

  useEffect(() => {
    const fetchCoinData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `http://127.0.0.1:8000/api/portfolio/coin-chart?asset=${coinSymbol}&days=${days}`
        );

        if (!response.ok) {
          throw new Error(
            `Error fetching data for ${coinSymbol}. Please contact the administrator.`
          );
        }

        const data = await response.json();
        if (!data || !Array.isArray(data)) {
          throw new Error("Invalid price data received.");
        }

        // Format data for Recharts
        const formattedData = data.map(([timestamp, price]) => {
          // Convert to a float so Recharts recognizes it as numeric
          const numericPrice = parseFloat(price);

          return {
            date: new Date(timestamp).toLocaleDateString(),
            price: numericPrice,
          };
        });

        // Optional: sort by date if not already sorted
        // formattedData.sort((a, b) => new Date(a.date) - new Date(b.date));

        setChartData(formattedData);

        // Calculate percentage change
        if (formattedData.length > 1) {
          const firstPrice = formattedData[0].price;
          const lastPrice =
            formattedData[formattedData.length - 1].price;

          if (firstPrice !== 0) {
            const diffPercent =
              ((lastPrice - firstPrice) / firstPrice) * 100;
            setPercentageChange(diffPercent);
          } else {
            setPercentageChange(0);
          }
        } else {
          // If there's only one data point or none
          setPercentageChange(0);
        }
      } catch (err) {
        setError(err.message);
        setChartData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCoinData();
  }, [coinSymbol, days]);

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {/* Title */}
        <h2>
          {coinSymbol.toUpperCase()} Price Chart (Last {days} Days)
        </h2>

        {/* Percentage Change Display */}
        <div className="price-change-container">
          <span>Price Change: </span>
          <span
            style={{
              color: percentageChange >= 0 ? "green" : "red",
              fontWeight: "bold",
            }}
          >
            {percentageChange >= 0 ? "+" : ""}
            {percentageChange.toFixed(2)}%
          </span>
        </div>

        {/* Dropdown to select the number of days */}
        <label htmlFor="days-select">Select Days:</label>
        <select
          id="days-select"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        >
          {[...Array(30)].map((_, i) => (
            <option key={i + 1} value={i + 1}>
              {i + 1} Days
            </option>
          ))}
        </select>

        {/* Loading / Error / Chart */}
        {loading ? (
          <p className="loading-message">Loading data...</p>
        ) : error ? (
          <p className="error-message">{error}</p>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart
              data={chartData}
              margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#16c784" stopOpacity={0.7} />
                  <stop offset="95%" stopColor="#16c784" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis
                dataKey="date"
                tick={{ fill: "#ccc", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "#ccc", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#222",
                  borderRadius: "5px",
                  color: "#fff",
                  border: "none",
                }}
                labelStyle={{ color: "#fff" }}
                itemStyle={{ color: "#fff" }}
              />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#16c784"
                fill="url(#priceGradient)"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
                animationDuration={800}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {/* Close Button */}
        <button className="close-button" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default CoinChartModel;
