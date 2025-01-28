import React, { useState } from 'react';
import { FaSort } from 'react-icons/fa';
import './RecentTransactions.css';

const RecentTransactions = () => {
  const [transactions, setTransactions] = useState([
    { name: 'BTC', currentPrice: '$50,000', buy: '$45,000', sold: '-', roi: 12, date: '2025-01-20' },
    { name: 'ETH', currentPrice: '$1,000', buy: '$800', sold: '$1,200', roi: 50, date: '2025-01-18' },
    { name: 'SUI', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'LIT', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'PLUME', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'W', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'BTC', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'XRP', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'ADA', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'DOT', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'MINA', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'DOGE', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'TRUMP', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'FLOW', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'Secret', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'FET', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    { name: 'CloudC', currentPrice: '$200', buy: '$180', sold: '-', roi: 11, date: '2025-01-15' },
    // Add more transactions as needed
  ]);
  const [sortOrder, setSortOrder] = useState('asc');

  const sortROI = () => {
    const sortedTransactions = [...transactions].sort((a, b) => {
      if (sortOrder === 'asc') {
        return a.roi - b.roi;
      } else {
        return b.roi - a.roi;
      }
    });
    setTransactions(sortedTransactions);
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div className="recent-transactions">
      <h3 className="transactions-title">Recent Transactions</h3>
      <div className="transactions-table-container">
        <table className="transactions-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Current Price</th>
              <th>Buy</th>
              <th>Sold</th>
              <th className="roi-header" onClick={sortROI}>
                ROI <FaSort />
              </th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {transactions.slice(0, 15).map((transaction, index) => (
              <tr key={index}>
                <td>{transaction.name}</td>
                <td>{transaction.currentPrice}</td>
                <td>{transaction.buy}</td>
                <td>{transaction.sold}</td>
                <td>{transaction.roi}%</td>
                <td>{transaction.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RecentTransactions;