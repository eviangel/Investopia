import React from 'react';
import './MarketStats.css';

const MarketStats = () => {
  return (
    <div className="market-stats">
      <h3 className="stats-title">Bitcoin USD (BTC-USD)</h3>
      <p className="stats-value">$16,430.00 <span className="stats-change">(+3.02%)</span></p>
      <div className="chart">
        <p>Chart Visualization</p>
      </div>
      <table className="stats-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Trading Volume</th>
            <th>Market Cap</th>
            <th>Holders</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>BitTeo</td>
            <td>$0.00000231</td>
            <td>$9,152,921</td>
            <td>$432,624,043</td>
            <td>18,212</td>
            <td><button className="trade-button">Trade</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default MarketStats;