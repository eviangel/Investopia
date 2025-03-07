import React from 'react';
import Sidebar from '../components/Sidebar';
import Dashboard from '../components/Dashboard';
import About from '../components/About';
import Docs from '../components/Docs';
import SignIn from '../components/SignIn';
import DailyPerformance from '../components/dailyperformance.jsx';
import { Route, Routes, useLocation } from 'react-router-dom';
import BalanceInfo from '../components/BalanceInfo';
import Login from "../components/Login";
import './App.css';
// import '../dailyperformance.css';
// import TransactionsChart from "../components/TransactionsChart";
// import TransactionsTabs from "../components/TransactionsTabs";
import Notifications from '../components/Notifications.jsx';

function App() {
  const location = useLocation();

  // // Hide Sidebar when on /daily_performance
  // const isPerformancePage = location.pathname.toLowerCase() === "/dailyperformance";


  return (
    <div className="app">
      <Sidebar /> {/* Sidebar always rendered */}
      {/* {!isPerformancePage && <Sidebar />} Hide sidebar on Daily Performance page */}
      <div className="main-content">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Dashboard userId={2}/>} />
          <Route path="/about" element={<About />} />
          <Route path="/docs" element={<Docs />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/dailyperformance" element={<DailyPerformance  />} />
          {/* <Route path="/transactions" element={<TransactionsChart />} /> */}
          <Route path="/Notifications" element={<Notifications />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
