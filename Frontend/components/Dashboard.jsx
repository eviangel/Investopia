import React from 'react';
import './Dashboard.css';
import MarketStats from './MarketStats';
import RecentTransactions from './RecentTransactions';
import AiRecommendations from './AiRecommendations';
import News from './News';
import BalanceInfo from './BalanceInfo';
// import UpgradeBanner from './UpgradeBanner';
import PortfolioChart from './PortfolioChart';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <div className="top-section">
        <BalanceInfo />
        {/* <UpgradeBanner /> */}
      </div>
      <div className="chart-section">
        <PortfolioChart />
      </div>
      <div className="main-section">
        {/* <MarketStats /> */}
        <RecentTransactions />
      </div>
      <div className="side-section">
        <AiRecommendations />
        <News />
      </div>
    </div>
  );
};

export default Dashboard;