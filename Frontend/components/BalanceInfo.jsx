import React, { useState,useEffect } from 'react';
import './BalanceInfo.css';
import AddTrade from './AddTrade';
import AddExchange from './AddExchange';
import CoinChartModel from './CoinChartModel';

const BalanceInfo = ({ userId }) => {
  const [showAddTrade, setShowAddTrade] = useState(false);
  const [showAddExchange, setShowAddExchange] = useState(false);
  const [totalBalance, setTotalBalance] = useState(null);
  const [dailyPnL, setDailyPnL] = useState(null);
  const [bestPerformer, setBestPerformer] = useState(null);
  const [worstPerformer, setWorstPerformer] = useState(null);
  const [selectedCoin, setSelectedCoin] = useState(null);


  const getDynamicColor = (value) => {
    if (!value) return '#ccc'; // Default neutral color
    if (parseFloat(value) < 0) return '#e74c3c'; // Red for negative values
    if (parseFloat(value) > 0) return '#16a085'; // Green for positive values
    return '#f1c40f'; // Yellow for neutral values
  };

  // Fetch Daily PnL from API
  useEffect(() => {
    const fetchDailyPerformance = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/portfolio/daily-performance?user_id=${userId}`);
        const data = await response.json();

        if (data.total_balance !== undefined) {
          setTotalBalance(data.total_balance);
        }

        if (data.daily_pnl !== undefined) {
          setDailyPnL(data.daily_pnl); // Set the daily PnL
        }
        if (data.best_performer) {
          setBestPerformer(data.best_performer); // Set the best performer data
        }
        if (data.worst_performer) {
          setWorstPerformer(data.worst_performer); // Set the worst performer data
        }
      } catch (error) {
        console.error("Error fetching daily performance:", error);
      }
    };

    fetchDailyPerformance();
  }, [userId]);

  const handleOpenAddTrade = () => {
    setShowAddTrade(true);
  };

  const handleCloseAddTrade = () => {
    setShowAddTrade(false);
  };

  const handleOpenAddExchange = () => {
    setShowAddExchange(true);
  };

  const handleCloseAddExchange = () => {
    setShowAddExchange(false);
  };
  const handleOpenChart = (coinSymbol) => {
    if (!coinSymbol) return; // Prevent setting undefined
    setSelectedCoin(coinSymbol);
  };

  return (
    <div className="balance-info">
      <div className="balance-section">
        <h3 className="balance-title">Total Balance</h3>
        <p className="balance-value">
          {totalBalance !== null ? `$${totalBalance.toFixed(2)}` : 'Loading...'}
        </p>
        
        {/* Display Daily PnL dynamically */}
        {dailyPnL !== null && (
          <span 
            className="balance-change" 
            style={{ color: getDynamicColor(dailyPnL) }}
          >
            Today's PnL: ${dailyPnL}
          </span>
        )}
      </div>

      <div className="performer-container">
        <div
          className="performer-box best-performer"
          onClick={() => handleOpenChart(bestPerformer?.Asset)}
        >
          <h4>Best Performer</h4>
          {bestPerformer && (
            <>
            <p>{bestPerformer.Asset}: +{bestPerformer.Gain_Loss_Percentage.toFixed(2)}%</p>
            <p>Total Value: ${bestPerformer.Total_Value.toFixed(2)}</p>
            <p>Portfolio: {bestPerformer.Portfolio_Percentage.toFixed(2)}%</p>
            </>
          )}
        </div>

        <div
          className="performer-box worst-performer"
          onClick={() => handleOpenChart(worstPerformer?.Asset)}
        >
          <h4>Worst Performer</h4>
          {worstPerformer && (
            <>
            <p>{worstPerformer.Asset}: {worstPerformer.Gain_Loss_Percentage.toFixed(2)}%</p>
            <p>Total Value: ${worstPerformer.Total_Value.toFixed(2)}</p>
            <p>Portfolio: {worstPerformer.Portfolio_Percentage.toFixed(2)}%</p>
            </>
          )}
        </div>
      </div>

      {selectedCoin && <CoinChartModel coinSymbol={selectedCoin} onClose={() => setSelectedCoin(null)} />}
    {/* </div>
      {selectedCoin && <CoinChartModel coin={selectedCoin.toLowerCase()} onClose={() => setSelectedCoin(null)} />}
      <div className="buttons-right">
        <button className="action-button" onClick={() => setShowAddTrade(true)}>
          Add Trade
        </button>
        <button className="action-button" onClick={() => setShowAddExchange(true)}>
          Add Exchange
        </button>
      </div> */}
{/* 
      {showAddTrade && <AddTrade onClose={() => setShowAddTrade(false)} />}
      {showAddExchange && <AddExchange onClose={() => setShowAddExchange(false)} />} */}
    </div>
  );
};

export default BalanceInfo;


