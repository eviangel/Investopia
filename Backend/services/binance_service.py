from datetime import datetime
from binance.spot import Spot as Client

class BinanceService:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def get_account_snapshot(self):
        try:
            return self.client.account_snapshot("SPOT")
        except Exception as e:
            print(f"Error fetching account snapshot: {e}")
            return {}

    def get_trade_history(self, symbol):
        try:
            return self.client.my_trades(symbol=symbol)
        except Exception as e:
            print(f"Error fetching trade history for {symbol}: {e}")
            return []

    def get_coin_price(self, coin):
        try:
            timestamp = int(datetime.timestamp(datetime.utcnow()) * 1000)
            candles = self.client.klines(
                symbol=f"{coin}USDT",
                interval="1m",
                startTime=timestamp,
                endTime=timestamp + 60000,
            )
            if candles:
                return float(candles[0][1])  # Open price
            return 0
        except Exception as e:
            print(f"Error fetching price for {coin}: {e}")
            return 0
