//
// 1) Common Filters
//
Vue.filter('toFixed', (num, asset) => {
  let fixedNum = Number(num).toFixed(asset === 'USDT' ? 3 : 8);
  return parseFloat(fixedNum); // Removes unnecessary zeros
});

Vue.filter('toMoney', num => {
  return Number(num).toFixed(0).replace(/./g, (c, i, a) => {
    return i && c !== '.' && ((a.length - i) % 3 === 0) ? ',' + c : c;
  });
});

//
// 2) Main Vue App
//
new Vue({
  el: '#app',
  data: {
    // WebSocket endpoint
    endpoint: 'wss://stream.binance.com:9443/ws/!ticker@arr',
    watchlist: [],
    status: 0,
    sock: null,
    cache: {},
    coins: [],
    dataRefreshInterval: null, // Timer for refreshing data,
    sortBy: "profitLossPercent",
    sortDirection: "desc",
    filterLowValue: false,
    displayMode: "grid",
    searchQuery: "",
    settingsOpen: false,
    showDetails: false,
    selectedCoin: null,
    pieChartInstance: null,
    username: "",
    password: "",
    isLoggedIn: false,
    userId: null,
    loginError: "",
    hardcodedPassword: "ktkt123",
    hardcodedPassword2: "pewd333",

  },

  computed: {
    sortedCoins() {
      return this.coins
        .slice()
        .filter(asset => {
          let totalValue = parseFloat(asset.totalValue) || 0;
          let matchesSearch = asset.token.toLowerCase().includes(this.searchQuery.toLowerCase());
          return matchesSearch && !(this.filterLowValue && totalValue < 10);
          // return !(this.filterLowValue && totalValue < 10); // Only filter if checkbox is checked
        })
        .map(asset => {
          let close = parseFloat(asset.close) || 0;
          let amount = parseFloat(asset.amount) || 0;
          let avgPrice = parseFloat(asset.avgPrice) || 0;
          let totalInvested = amount * avgPrice;
          let currentValue = amount * close;
          let percent = parseFloat(asset.percent) || 0; // Coin Daily Performance
          let profitLoss = currentValue - totalInvested;
          let profitLossPercent = totalInvested > 0 ? (profitLoss / totalInvested) * 100 : 0;
    
          // ✅ Determine styling dynamically based on active filter
          let isAssetPerf = this.sortBy === 'profitLossPercent';
          let style = isAssetPerf
            ? profitLossPercent > 0 ? 'gain' : profitLossPercent < 0 ? 'loss' : ''
            : percent > 0 ? 'gain' : percent < 0 ? 'loss' : '';
    
          return {
            ...asset,
            close,
            amount,
            avgPrice,
            profitLoss: parseFloat(profitLoss.toFixed(2)), // Ensure it's a number
            profitLossPercent: parseFloat(profitLossPercent.toFixed(2)), // Ensure it's a number
            percent: parseFloat(percent.toFixed(2)), // Ensure it's a number
            style,
          };
        })
        .sort((a, b) => {
          let aValue = parseFloat(a[this.sortBy]) || 0;
          let bValue = parseFloat(b[this.sortBy]) || 0;
          
          return this.sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
        });
    }
  },

  methods: {

    selectCoin(coin) {
      this.selectedCoin = coin;
      this.generatePieChart();
      this.$nextTick(() => {
        this.generatePieChart();
      });
    },
  
    generatePieChart() {
      if (!this.selectedCoin) return;

    // ✅ Ensure the canvas element exists before getting context
    const canvas = document.getElementById("pieChart");
    if (!canvas) {
      console.error("Pie chart canvas not found!");
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      console.error("Unable to get canvas context!");
      return;
    }

    // ✅ Destroy previous chart instance to prevent duplication
    if (this.pieChartInstance) {
      this.pieChartInstance.destroy();
    }

    const portfolioData = [
      this.selectedCoin.portfolioPercentage, 
      100 - this.selectedCoin.portfolioPercentage
    ];
    const labels = [this.selectedCoin.token, "Other Assets"];
    const colors = ["#02B3E7", "#CFD3D6"];

    this.pieChartInstance = new Chart(ctx, {
      type: "pie",
      data: {
        labels: labels,
        datasets: [{
          data: portfolioData,
          backgroundColor: colors,
          borderColor: "#fff",
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
            position: "right",
          },
        }
      }
    });
    },




    toggleDisplayMode() {
      this.displayMode = this.displayMode === "grid" ? "table" : "grid";
    },
    getFontSize(token) {
      let length = token.length;
      if (length > 7) {
        return "1em"; // Smallest font for long names
      } else if (length > 5) {
        return "1.2em"; // Medium font for medium-length names
      } else {
        return "1.5em"; // Default font for short names
      }
    },

    fetchPairs() {
      if (!this.userId) {
        console.warn("⚠️ No user is logged in, skipping fetch.");
        return;
      }

      // fetch(`http://79.211.167.133:8000/api/portfolio/user-assets?user_id=${this.userId}`)
      fetch(`http://127.0.0.1:8000/api/portfolio/user-assets?user_id=${this.userId}`)
      .then(response => response.json())
        .then(data => {
          console.log("Full Backend Response:", data);
    
          if (!Array.isArray(data)) {
            console.error("Invalid API response: Expected an array, got:", data);
            return;
          }
    
          // ✅ Store API assets in watchlist (formatted for Binance)
          this.watchlist = data.map(asset => `${asset.Asset.toUpperCase()}USDT`);
    
          console.log("Processed Watchlist for Binance:", this.watchlist);
    
          const newCoins = data.map(asset => ({
            symbol: asset.Asset.toUpperCase(),
            token: asset.Asset.toUpperCase(),
            close: parseFloat(asset.Today_Price) || 0, // Use API price initially
            amount: parseFloat(asset.Amount) || 0,
            avgPrice: parseFloat(asset.Average_Price) || 0,
            totalValue: parseFloat(asset.Total_Value) || 0,
            portfolioPercentage: parseFloat(asset.Portfolio_Percentage) || 0,
            icon: `https://raw.githubusercontent.com/eviangel/Crypto_icons/main/icons/${asset.Asset.toLowerCase()}.png`,
          }));
    
          // ✅ Ensure Vue reactivity
          this.$set(this, "coins", newCoins);
    
          if (this.watchlist.length > 0) {
            this.startAutoRefresh();
          } else {
            console.error("No valid pairs received from backend!");
          }
        })
        .catch(error => console.error("Error fetching pairs:", error));
    },

    startAutoRefresh() {
      this.fetchBinanceData(); // Fetch Binance data on startup
    
      if (this.dataRefreshInterval) {
        clearInterval(this.dataRefreshInterval);
      }
    
      this.dataRefreshInterval = setInterval(() => {
        console.log("🔄 Refreshing Binance WebSocket Data...");
        this.fetchBinanceData(); // Fetch new prices every x minute
        this.applyCachedUpdates(); // Apply stored price updates every x minute
      }, 600000);
    },
      applyCachedUpdates() {
        Object.keys(this.cache).forEach(token => {
          let assetIndex = this.coins.findIndex(a => a.token === token);
          if (assetIndex !== -1) {
            this.$set(this.coins[assetIndex], 'close', this.cache[token].close);
            this.$set(this.coins[assetIndex], 'change', this.cache[token].change);
            this.$set(this.coins[assetIndex], 'percent', this.cache[token].percent);
          }
        });
      
        console.log("✅ Applied cached Binance price updates:", this.coins);
    },

    fetchBinanceData() {
      if (this.watchlist.length === 0) {
        console.warn("WebSocket not started because watchlist is empty.");
        return;
      }
    
      let streams = this.watchlist.map(symbol => `${symbol.toLowerCase()}@ticker`).join("/");
      let endpoint = `wss://stream.binance.com:9443/ws/${streams}`;
    
      if (this.sock) {
        console.info("🛑 Closing existing WebSocket before starting a new one...");
        this.sock.close();
      }
    
      this.sock = new WebSocket(endpoint);
      console.info("✅ WebSocket Connected:", endpoint);
    
      // ✅ Track received updates for each asset
      this.receivedUpdates = new Set();
    
      this.sock.addEventListener("message", (e) => {
        this.onSockData(e);
    
        // ✅ Close WebSocket only after all assets receive at least one update
        if (this.receivedUpdates.size >= this.watchlist.length) {
          console.info("🛑 WebSocket Closing: All assets received an update.");
          this.sock.close();
        }
      });
    
      this.sock.addEventListener("close", () => {
        console.info("🛑 WebSocket Disconnected.");
      });
    
      this.sock.addEventListener("error", err => console.error("❌ WebSocket Error:", err));

      // ✅ Force WebSocket to close after 1 minute if not all assets update
      setTimeout(() => {
        if (this.sock && this.sock.readyState === WebSocket.OPEN) {
          console.warn("⚠️ WebSocket closing due to timeout: Not all assets received an update.");
          this.sock.close();
        }
      }, 10000); // Force close after 1 minute if updates are missing
    },

    onSockData(e) {
      let item = JSON.parse(e.data);
      let token = item.s.replace("USDT", "").toUpperCase(); // Convert Binance format to API format
    
      if (!this.watchlist.includes(item.s.toUpperCase())) {
        return; // ✅ Ignore updates that are not in the watchlist
      }
    
      let close = parseFloat(item.c) || 0;
      let change = parseFloat(item.p) || 0;
      let percent = parseFloat(item.P) || 0;
    
      // ✅ Store the latest price in cache
      this.cache[token] = { close, change, percent };
    
      // ✅ Apply cached update immediately to `this.coins`
      let assetIndex = this.coins.findIndex(a => a.token === token);
      if (assetIndex !== -1) {
        this.$set(this.coins[assetIndex], 'close', close);
        this.$set(this.coins[assetIndex], 'change', change);
        this.$set(this.coins[assetIndex], 'percent', percent);
      }
    
      // ✅ Track that this token received an update
      if (!this.receivedUpdates.has(token)) {
        this.receivedUpdates.add(token);
        console.log(`✅ Binance Price Updated for ${token}: Close=${close}, Change=${change}, Percent=${percent}`);
      }
      // ✅ Debug if not all assets received updates
      if (this.receivedUpdates.size < this.watchlist.length) {
        console.warn(`⚠️ Waiting for updates... Received: ${this.receivedUpdates.size}/${this.watchlist.length}`);
      }
    },

    onImgError(e) {
      // e is the error event; e.target is the <img> element
      const defaultIcon = 'https://raw.githubusercontent.com/eviangel/Crypto_icons/main/icons/default.png';
      e.target.src = defaultIcon;
    },

    getCoinData(item) {
      let symbol = (item.s || '').toUpperCase();
      let token = symbol.replace(/USDT$/, '');
      let amount = this.cache[symbol] ? this.cache[symbol].amount : 0;
      let avgPrice = this.cache[symbol] ? parseFloat(this.cache[symbol].avgPrice) || 0 : 0;
      avgPrice = avgPrice < 0.000001 ? avgPrice : avgPrice.toFixed(8);
      let open = parseFloat(item.o) || 0;
      let high = parseFloat(item.h) || 0;
      let low = parseFloat(item.l) || 0;
      let close = parseFloat(item.c) || 0;
      let change = parseFloat(item.p) || 0;
      let percent = parseFloat(item.P) || 0;
      let pair = token + '/USDT';
      let style = percent > 0 ? 'gain' : percent < 0 ? 'loss' : '';
      let totalInvested = amount * avgPrice;
      let currentValue = amount * close;
      let profitLoss = currentValue - totalInvested;
      profitLoss = profitLoss.toFixed(2);
      let profitLossPercent = totalInvested > 0 ? (profitLoss / totalInvested) * 100 : 0;
      let portfolioPercentage = this.cache[symbol] ? this.cache[symbol].portfolioPercentage || 0 : 0;
    
      // ✅ Correct icon assignment
      let iconUrl = `https://raw.githubusercontent.com/eviangel/Crypto_icons/main/icons/${token.toLowerCase()}.png`;
      let defaultIcon = `https://raw.githubusercontent.com/eviangel/Crypto_icons/main/icons/default.png`;
    
      return {
        symbol, token, pair, open, high, low, close, change, percent, amount, avgPrice,
        icon: iconUrl, style, totalInvested, currentValue, profitLoss, profitLossPercent, portfolioPercentage
      };
    },

  },
  watch: {
    coins: {
      deep: true,
      handler() {
        this.generatePieChart();
      }
    }
  },
  mounted() {
    window.addEventListener("message", (event) => {
      if (event.data && event.data.userId) { // ✅ Only process messages that contain userId
        console.log("✅ Vue received userId:", event.data.userId);
        this.userId = event.data.userId;
        this.isLoggedIn = true;
        this.fetchPairs(); // ✅ Fetch data after getting userId
      } else {
        console.warn("⚠️ Ignored message:", event.data); // ✅ Log ignored messages
      }
    });
  },

  beforeDestroy() {
    if (this.dataRefreshInterval) {
      clearInterval(this.dataRefreshInterval);
    }
    if (this.sock) {
      this.sock.close();
    }
  }
});
