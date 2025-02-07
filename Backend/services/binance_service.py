from datetime import datetime
from binance.spot import Spot as Client
import requests
import redis
import json
from services.coingecko_service import CoinGeckoService

class BinanceService:
    def __init__(self, api_key=None, api_secret=None):
        # self.client = Client(api_key, api_secret)
        self.client = Client(api_key, api_secret) if api_key and api_secret else None
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

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
        Fetch the price of an asset from Binance, falling back to CoinGecko.
        If both fail, returns None so the asset can be ignored.

        Parameters:
        - asset: The asset name (e.g., BTC).
        - price_type: Type of price to fetch.
          - "current" (default): Fetch the latest trading price.
          - "yesterday": Fetch the previous day's closing price.

        Returns:
        - The price as a float, or None if not found.
        """
        try:
            # Try fetching from Binance
            if price_type == "current":
                url = f'https://api.binance.com/api/v3/ticker/price?symbol={asset}USDT'
            elif price_type == "yesterday":
                url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={asset}USDT'
            else:
                raise ValueError(f"Invalid price_type '{price_type}'. Use 'current' or 'yesterday'.")

            response = requests.get(url)
            if response.status_code == 400:
                print(f"Warning: {asset} is not available on Binance. Trying CoinGecko.")
                return CoinGeckoService.get_price(asset)  # Now calls CoinGecko

            response.raise_for_status()
            data = response.json()
            return float(data['price']) if price_type == "current" else float(data['prevClosePrice'])

        except Exception as e:
            print(f"Error fetching {price_type} price for {asset}: {e}")
            return CoinGeckoService.get_price(asset)  # Now calls CoinGecko

    def get_all_prices(self):
        """
        Fetches all Binance USDT prices in a single request and caches them.

        Returns:
        - A dictionary of asset prices, e.g., {"BTC": 100000, "ETH": 2200}.
        """
        try:
            # Check Redis cache
            cached_prices = self.redis_client.get("binance_prices")
            if cached_prices:
                return json.loads(cached_prices)

            # Fetch from Binance API
            url = 'https://api.binance.com/api/v3/ticker/price'
            response = requests.get(url)
            response.raise_for_status()
            prices = response.json()

            # Convert to dictionary { "BTC": 32000, "ETH": 2200, ... }
            price_dict = {item["symbol"].replace("USDT", ""): float(item["price"]) for item in prices if item["symbol"].endswith("USDT")}

            # Cache for 60 seconds
            self.redis_client.setex("binance_prices", 60, json.dumps(price_dict))

            return price_dict
        except Exception as e:
            print(f"Error fetching bulk prices from Binance: {e}")
            return {}

    def get_price_from_cache(self, asset):
        """
        Gets a coin's price from Redis cache or fetches from Binance if missing.

        Parameters:
        - asset: The asset name (e.g., BTC).

        Returns:
        - The price of the asset as a float, or None if not found.
        """
        try:
            # Check if prices are cached
            cached_prices = self.redis_client.get("binance_prices")
            if cached_prices:
                price_dict = json.loads(cached_prices)
                return price_dict.get(asset, None)

            # Fetch new prices if not in cache
            price_dict = self.get_all_prices()
            return price_dict.get(asset, None)

        except Exception as e:
            print(f"Error getting cached price for {asset}: {e}")
            return None

    @staticmethod
    def calculate_average_entry_price(transactions):
        total_coins = 0
        total_usd_paid = 0

        for transaction in transactions:
            action = transaction['isBuyer']
            amount = float(transaction['qty'])
            price = float(transaction['price'])

            if action:  # If the transaction is a buy
                total_coins += amount
                total_usd_paid += amount * price
            else:  # If the transaction is a sell
                # Adjust the total USD paid based on the proportion of coins sold
                if total_coins > 0:
                    average_price_before_sale = total_usd_paid / total_coins
                    usd_value_of_sold_coins = amount * average_price_before_sale
                    total_usd_paid -= usd_value_of_sold_coins
                    total_coins -= amount

        return total_usd_paid / total_coins if total_coins > 0 else 0  # Avoid division by zero

    def check_average_price(self, asset):
        try:
            transactions = self.client.my_trades(symbol=f"{asset}USDT")
            
            # Convert transactions to a list of dictionaries
            formatted_transactions = [{
                'isBuyer': tx['isBuyer'],
                'qty': tx['qty'],
                'price': tx['price']
            } for tx in transactions]

            # Calculate the average entry price
            avg_price = self.calculate_average_entry_price(formatted_transactions)
            print(f"✅ Average Entry Price for {asset}: {avg_price}")
            return avg_price

        except Exception as e:
            print(f"Error fetching transactions for {asset}: {e}")
            return 0  # Default to 0 if no trade history is available   