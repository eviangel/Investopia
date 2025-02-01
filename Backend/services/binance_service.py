from datetime import datetime
from binance.spot import Spot as Client
import requests

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

    # def get_coin_price(self, coin):
    #     try:
    #         timestamp = int(datetime.timestamp(datetime.utcnow()) * 1000)
    #         candles = self.client.klines(
    #             symbol=f"{coin}USDT",
    #             interval="1m",
    #             startTime=timestamp,
    #             endTime=timestamp + 60000,
    #         )
    #         if candles:
    #             return float(candles[0][1])  # Open price
    #         return 0
    #     except Exception as e:
    #         print(f"Error fetching price for {coin}: {e}")
    #         return 0


    @staticmethod
    def get_coin_price(asset, price_type="current"):
        """
        Fetch the price of an asset from Binance.

        Parameters:
        - asset: The asset name (e.g., BTC).
        - price_type: Type of price to fetch. Options:
          - "current" (default): Fetch the latest trading price.
          - "yesterday": Fetch the yesterday closing price.

        Returns:
        - The requested price as a float, or None if the request fails.
        """
        try:
            if price_type == "current":
                url = f'https://api.binance.com/api/v3/ticker/price?symbol={asset}USDT'
            elif price_type == "yesterday":
                url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={asset}USDT'
            else:
                raise ValueError(f"Invalid price_type '{price_type}'. Use 'current' or 'yesterday'.")

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            # Extract correct price based on type
            if price_type == "current":
                return float(data['price'])
            elif price_type == "yesterday":
                return float(data['prevClosePrice'])

        except Exception as e:
            print(f"Error fetching {price_type} price for {asset}: {e}")
            return None