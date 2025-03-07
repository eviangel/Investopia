import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const TransactionsChart = () => {
  const [data, setData] = useState([]);
  const userId = localStorage.getItem("userId");
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/transactions/getuser_deposits_withdraw_${userId}`)
      .then((response) => response.json())
      .then((jsonData) => {
        // Combine withdrawals and deposits
        const transactions = [...jsonData.withdrawals, ...jsonData.deposits];
        
        // Convert time to Date and sort
        const formattedData = transactions.map(t => ({
          date: new Date(t.time).toISOString().split("T")[0], // Keep only YYYY-MM-DD
          quantity: parseFloat(t.quantity),
          action: t.action
        })).sort((a, b) => new Date(a.date) - new Date(b.date));

        // Aggregate by date
        const aggregatedData = formattedData.reduce((acc, transaction) => {
          const existing = acc.find(t => t.date === transaction.date);
          if (existing) {
            existing[transaction.action] += transaction.quantity;
          } else {
            acc.push({ date: transaction.date, DEPOSIT: 0, WITHDRAW: 0, [transaction.action]: transaction.quantity });
          }
          return acc;
        }, []);

        setData(aggregatedData);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="DEPOSIT" stroke="#82ca9d" name="Deposits" />
        <Line type="monotone" dataKey="WITHDRAW" stroke="#ff6666" name="Withdrawals" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TransactionsChart;
