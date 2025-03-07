import React, { useState, useEffect, useMemo, useRef } from 'react';
import Chart from 'chart.js/auto';
import '../components/dailyperformance.scss';
import { useUser } from '../src/utils/UserContext';

const DailyPerformance = () => {
  const { userId } = useUser();

  // States (similar to Vue's data)
  const [coins, setCoins] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [sortBy, setSortBy] = useState("profitLossPercent");
  const [sortDirection, setSortDirection] = useState("desc");
  const [filterLowValue, setFilterLowValue] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [displayMode, setDisplayMode] = useState("grid");
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(!!userId);

  // Refs for Chart, WebSocket, intervals, cache and updates
  const chartRef = useRef(null);
  const pieChartInstanceRef = useRef(null);
  const sockRef = useRef(null);
  const dataRefreshIntervalRef = useRef(null);
  const cacheRef = useRef({});
  const receivedUpdatesRef = useRef(new Set());

  // Utility functions (mimicking Vue filters)
  const getFontSize = (token) => {
    if (token.length > 7) return "1em";
    if (token.length > 5) return "1.2em";
    return "1.5em";
  };

  const toMoney = (num) => {
    return Number(num)
      .toFixed(0)
      .replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  // Fetch asset pairs from the backend and initialize data
  const fetchPairs = () => {
    if (!userId) {
      console.warn("No user logged in, skipping fetch.");
      return;
    }
    fetch(`http://127.0.0.1:8000/api/portfolio/user-assets?user_id=${userId}`)
      .then((response) => response.json())
      .then((data) => {
        if (!Array.isArray(data)) {
          console.error("Invalid API response: Expected an array.");
          return;
        }
        const newWatchlist = data.map((asset) => `${asset.Asset.toUpperCase()}USDT`);
        setWatchlist(newWatchlist);
        const newCoins = data.map((asset) => ({
          symbol: asset.Asset.toUpperCase(),
          token: asset.Asset.toUpperCase(),
          close: parseFloat(asset.Today_Price) || 0,
          amount: parseFloat(asset.Amount) || 0,
          avgPrice: parseFloat(asset.Average_Price) || 0,
          totalValue: parseFloat(asset.Total_Value) || 0,
          portfolioPercentage: parseFloat(asset.Portfolio_Percentage) || 0,
          icon: `https://raw.githubusercontent.com/eviangel/Crypto_icons/main/icons/${asset.Asset.toLowerCase()}.png`
        }));
        setCoins(newCoins);
        if (newWatchlist.length > 0) {
          startAutoRefresh(newWatchlist);
        } else {
          console.error("No valid pairs received from backend!");
        }
      })
      .catch((error) => console.error("Error fetching pairs:", error));
  };

  // Start refreshing Binance data automatically
  const startAutoRefresh = (watchlistLocal) => {
    fetchBinanceData(watchlistLocal);
    if (dataRefreshIntervalRef.current) clearInterval(dataRefreshIntervalRef.current);
    dataRefreshIntervalRef.current = setInterval(() => {
      fetchBinanceData(watchlistLocal);
      applyCachedUpdates();
    }, 600000); // every 10 minutes
  };

  const applyCachedUpdates = () => {
    setCoins((prevCoins) =>
      prevCoins.map((coin) => {
        const cached = cacheRef.current[coin.token];
        return cached ? { ...coin, close: cached.close, change: cached.change, percent: cached.percent } : coin;
      })
    );
  };

  // Connect to Binance WebSocket and fetch live data
  const fetchBinanceData = (watchlistLocal) => {
    if (watchlistLocal.length === 0) {
      console.warn("WebSocket not started because watchlist is empty.");
      return;
    }
    const streams = watchlistLocal.map((symbol) => `${symbol.toLowerCase()}@ticker`).join("/");
    const endpoint = `wss://stream.binance.com:9443/ws/${streams}`;
    if (sockRef.current) {
      sockRef.current.close();
    }
    const sock = new WebSocket(endpoint);
    sockRef.current = sock;
    receivedUpdatesRef.current = new Set();

    sock.addEventListener("message", (e) => {
      onSockData(e, watchlistLocal);
      if (receivedUpdatesRef.current.size >= watchlistLocal.length) {
        sock.close();
      }
    });
    sock.addEventListener("close", () => console.info("WebSocket Disconnected."));
    sock.addEventListener("error", (err) => console.error("WebSocket Error:", err));

    // Force-close the socket if updates are missing after 30 seconds
    setTimeout(() => {
      if (sock && sock.readyState === WebSocket.OPEN) {
        sock.close();
      }
    }, 30000);
  };

  const onSockData = (e, watchlistLocal) => {
    try {
      const item = JSON.parse(e.data);
      const token = item.s.replace("USDT", "").toUpperCase();
      if (!watchlistLocal.includes(item.s.toUpperCase())) return;
      const close = parseFloat(item.c) || 0;
      const change = parseFloat(item.p) || 0;
      const percent = parseFloat(item.P) || 0;
      cacheRef.current[token] = { close, change, percent };
      setCoins((prevCoins) =>
        prevCoins.map((coin) =>
          coin.token === token ? { ...coin, close, change, percent } : coin
        )
      );
      if (!receivedUpdatesRef.current.has(token)) {
        receivedUpdatesRef.current.add(token);
      }
    } catch (error) {
      console.error("Error processing WebSocket data:", error);
    }
  };

  // When a coin is selected, store it to generate its pie chart
  const selectCoin = (coin) => {
    setSelectedCoin(coin);
  };


  function formatPrice(value) {
    if (!value || isNaN(value)) return "0";
  
    // Convert to number
    const num = Number(value);
  
    if (num >= 1) {
      // Up to 2 decimals
      let str = num.toFixed(2); 
      // Remove trailing zeros after decimal
      str = str.replace(/(\.\d*?[1-9])0+$/g, "$1");
      // If decimal becomes ".", remove it
      return str.replace(/\.$/, "");
    } else {
      // Up to 8 decimals for small values
      let str = num.toFixed(8); 
      // Remove trailing zeros after decimal
      str = str.replace(/(\.\d*?[1-9])0+$/g, "$1");
      // If decimal becomes ".", remove it
      return str.replace(/\.$/, "");
    }
  }


  // Toggle between grid and table display modes
  const toggleDisplayMode = () => {
    setDisplayMode((prev) => (prev === "grid" ? "table" : "grid"));
  };

  // Generate or update the pie chart when a coin is selected
  useEffect(() => {
    if (!selectedCoin) return;
    const canvas = chartRef.current;
    if (!canvas) {
      console.error("Pie chart canvas not found!");
      return;
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      console.error("Unable to get canvas context!");
      return;
    }
    if (pieChartInstanceRef.current) {
      pieChartInstanceRef.current.destroy();
    }
    const portfolioData = [
      selectedCoin.portfolioPercentage,
      100 - selectedCoin.portfolioPercentage
    ];
    const labels = [selectedCoin.token, "Other Assets"];
    const colors = ["#02B3E7", "#CFD3D6"];
    pieChartInstanceRef.current = new Chart(ctx, {
      type: "pie",
      data: {
        labels,
        datasets: [
          {
            data: portfolioData,
            backgroundColor: colors,
            borderColor: "#fff",
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
            position: "right"
          }
        }
      }
    });
  }, [selectedCoin]);

  // Compute the sorted coins (equivalent to Vue's computed property)
  const sortedCoins = useMemo(() => {
    return coins
      .filter((asset) => {
        const totalValue = parseFloat(asset.totalValue) || 0;
        const matchesSearch = asset.token.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesSearch && !(filterLowValue && totalValue < 10);
      })
      .map((asset) => {
        const close = parseFloat(asset.close) || 0;
        const amount = parseFloat(asset.amount) || 0;
        const avgPrice = parseFloat(asset.avgPrice) || 0;
        const totalInvested = amount * avgPrice;
        const currentValue = amount * close;
        const profitLoss = currentValue - totalInvested;
        const profitLossPercent = totalInvested > 0 ? (profitLoss / totalInvested) * 100 : 0;
        const percent = parseFloat(asset.percent) || 0;
        const isAssetPerf = sortBy === 'profitLossPercent';
        const style = isAssetPerf
          ? profitLossPercent > 0 ? 'gain' : profitLossPercent < 0 ? 'loss' : ''
          : percent > 0 ? 'gain' : percent < 0 ? 'loss' : '';
        return {
          ...asset,
          close,
          amount,
          avgPrice,
          profitLoss: parseFloat(profitLoss.toFixed(2)),
          profitLossPercent: parseFloat(profitLossPercent.toFixed(2)),
          percent: parseFloat(percent.toFixed(2)),
          style
        };
      })
      .sort((a, b) => {
        const aValue = parseFloat(a[sortBy]) || 0;
        const bValue = parseFloat(b[sortBy]) || 0;
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      });
  }, [coins, sortBy, sortDirection, filterLowValue, searchQuery]);

  // When the userId changes, fetch pairs and set up cleanup
  useEffect(() => {
    setIsLoggedIn(!!userId);
    if (userId) {
      fetchPairs();
    }
    return () => {
      if (dataRefreshIntervalRef.current) clearInterval(dataRefreshIntervalRef.current);
      if (sockRef.current) sockRef.current.close();
    };
  }, [userId]);

  return (
    <div id="app" className="daily-performance">
      {isLoggedIn ? (
        <>
          <header className="header-wrap">
            <div className="header-row flex-row flex-middle flex-space">
              <h1 className="text-nowrap text-condense shadow-text">Asset Performance</h1>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-dropdown"
              >
                <option value="profitLossPercent">Asset Performance</option>
                <option value="percent">Coin Daily Performance</option>
                <option value="portfolioPercentage">Portfolio %</option>
                <option value="totalValue">Total Value</option>
              </select>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for a coin..."
                className="search-box"
              />
              <select
                value={sortDirection}
                onChange={(e) => setSortDirection(e.target.value)}
                className="sort-direction-dropdown"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
              <div className="settings-dropdown">
                <button onClick={() => setSettingsOpen((prev) => !prev)} className="settings-btn">
                  ⚙️ Settings
                </button>
                {settingsOpen && (
                  <div className="settings-menu">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={filterLowValue}
                        onChange={(e) => setFilterLowValue(e.target.checked)}
                      />{" "}
                      Hide assets below $10
                    </label>
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={showDetails}
                        onChange={(e) => setShowDetails(e.target.checked)}
                      />{" "}
                      Show coin details
                    </label>
                  </div>
                )}
              </div>
              <button onClick={toggleDisplayMode} className="toggle-btn">
                Switch to {displayMode === "grid" ? "Table" : "Grid"} View
              </button>
            </div>
            {selectedCoin && (
              <div className="chart-container">
                <h2>{selectedCoin.token} Portfolio Share</h2>
                <canvas ref={chartRef} id="pieChart"></canvas>
                <button onClick={() => setSelectedCoin(null)} className="close-btn">
                  Close
                </button>
              </div>
            )}
            <a href="set-average-price.html" className="nav-btn">
              Set Average Price
            </a>
          </header>
          <main className="main-wrap">
            {displayMode === "grid" ? (
              <div className="main-grid-list">
                {sortedCoins.map((c) => (
                  <div
                    key={c.symbol}
                    className={`main-grid-item ${c.style}`}
                    onClick={() => selectCoin(c)}
                  >
                    <div className="main-grid-info flex-row flex-top flex-stretch">
                      <div className="push-right">
                        <img
                          src={c.icon}
                          alt={c.token}
                          onError={(e) => {
                            e.target.src =
                              'https://raw.githubusercontent.com/eviangel/Crypto_icons/main/icons/default.png';
                          }}
                        />
                      </div>
                      <div className="flex-1 shadow-text">
                        <div className="flex-row flex-top flex-space">
                          <div className="text-left text-clip push-right">
                            <h1
                              className="text-primary text-clip"
                              style={{ fontSize: getFontSize(c.token) }}
                            >
                              {c.token}
                              {c.asset && (
                                <small className="text-faded text-small text-condense">
                                  /{c.asset}
                                </small>
                              )}
                            </h1>
                            <h2 className="text-bright text-clip">
                              {formatPrice(c.close)}
                              {/* {parseFloat(c.close).toFixed(8)} */}
                            </h2>
                          </div>
                          <div className="text-right">
                            <div className={`color text-big text-clip ${c.style}`}>
                              {c.percent !== undefined ? c.percent + "%" : "0.00%"}
                              <small className="text-faded">Daily perf</small>
                            </div>
                            <div className={`color text-big text-clip ${c.style}`}>
                              {c.profitLossPercent.toFixed(2)}%
                              <small className="text-faded">Asset perf</small>
                            </div>
                            { (
                              <div className={`hidden-details ${showDetails ? 'show-always' : 'hover-enabled'}`}>
                                <div className="text-clip">
                                  {formatPrice(c.amount)}
                                  <small className="text-faded">Amount</small>
                                </div>
                                <div className="text-clip">
                                  {c.avgPrice}
                                  <small className="text-faded">Avg Price</small>
                                </div>
                                <div className="text-clip">
                                  {c.portfolioPercentage.toFixed(2)}%
                                  <small className="text-faded">Portfolio %</small>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <table className="coin-table">
                <thead>
                  <tr>
                    <th>Coin</th>
                    <th>Price</th>
                    <th>Asset Perf (%)</th>
                    <th>Daily Perf (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedCoins.map((c) => (
                    <tr key={c.symbol} className={c.style}>
                      <td>{c.token}</td>
                      <td>{formatPrice(c.close)}</td>
                      <td>{c.profitLossPercent.toFixed(2)}%</td>
                      <td>{c.percent.toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </main>
        </>
      ) : (
        <p>Loading user data...</p>
      )}
    </div>
  );
};

export default DailyPerformance;
