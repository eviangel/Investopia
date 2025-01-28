import React, { useState } from 'react';
import './BalanceInfo.css';
import AddTrade from './AddTrade';
import AddExchange from './AddExchange';

const BalanceInfo = () => {
  const [showAddTrade, setShowAddTrade] = useState(false);
  const [showAddExchange, setShowAddExchange] = useState(false);

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

  return (
    <div className="balance-info">
      <div className="balance-section">
        <h3 className="balance-title">Total Balance</h3>
        <p className="balance-value">$78,820.00</p>
        <span className="balance-change">+ $931.12</span>
      </div>

      <div className="performer-container">
        <div className="performer-box best-performer">
          <h4>Best Performer</h4>
          <p>BTC: +7.5%</p>
        </div>
        <div className="performer-box worst-performer">
          <h4>Worst Performer</h4>
          <p>ETH: -3.2%</p>
        </div>
      </div>

      <div className="buttons-right">
        <button className="action-button" onClick={handleOpenAddTrade}>
          Add Trade
        </button>
        <button className="action-button" onClick={handleOpenAddExchange}>
          Add Exchange
        </button>
      </div>

      {showAddTrade && <AddTrade onClose={handleCloseAddTrade} />}
      {showAddExchange && <AddExchange onClose={handleCloseAddExchange} />}
    </div>
  );
};

export default BalanceInfo;


