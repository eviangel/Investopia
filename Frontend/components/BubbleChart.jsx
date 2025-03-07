import React, { useEffect, useState } from "react";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList, ZAxis } from "recharts";

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip" style={{ background: "white", padding: "10px", border: "1px solid #ccc", borderRadius: "5px", color: "black" }}>
        <p><strong>Asset:</strong> {payload[0].payload.Asset}</p>
        <p><strong>Profit:</strong> {payload[0].payload.Profit}</p>
        <p><strong>Profit Percentage:</strong> {payload[0].payload.Profit_Percentage}%</p>
        <p><strong>Portfolio Percentage:</strong> {payload[0].payload.Portfolio_Percentage}%</p>
      </div>
    );
  }
  return null;
};

const BubbleChart = ({userId}) => {
  const [data, setData] = useState([]);
  const [maxPortfolioPercentage, setMaxPortfolioPercentage] = useState(1);
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/portfolio/top-worst-assets?user_id=${userId}`)
      .then((response) => response.json())
      .then((apiData) => {
        console.log("API Data:", apiData); // Debugging log

        // Find max portfolio percentage for scaling
        const maxPortfolio = Math.max(...apiData.top_assets.map(a => a.Portfolio_Percentage), ...apiData.worst_assets.map(a => a.Portfolio_Percentage));
        setMaxPortfolioPercentage(maxPortfolio || 1); // Avoid division by zero

        // Normalize data for better visualization
        let processedData = [...apiData.top_assets, ...apiData.worst_assets].map(asset => ({
          ...asset,
          Profit: asset.Profit,
          Profit_Percentage: asset.Profit_Percentage > 1000 ? 1000 + Math.log(asset.Profit_Percentage - 999) * 50 : asset.Profit_Percentage, // Log scaling for extreme values
          BubbleSize: (asset.Portfolio_Percentage / maxPortfolio) * 300 + 10 // Ensure a minimum size and scale properly
        }));

        console.log("Processed Data:", processedData); // Debugging log

        setData(processedData);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" dataKey="Profit" name="Profit" />
        <YAxis type="number" dataKey="Profit_Percentage" name="Profit Percentage" />
        <ZAxis type="number" dataKey="BubbleSize" range={[10, 400]} />
        <Tooltip content={<CustomTooltip />} />
        <Scatter name="Assets" data={data} fill="#8884d8" shape="circle">
          <LabelList dataKey="Asset" position="top" fontSize={12} />
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );
};

export default BubbleChart;
