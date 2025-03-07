import requests
from db.db_handler import DatabaseHandler
from services.redis_service import RedisService
import time
import json

class CoinGeckoService:
    BASE_URL = "https://api.coingecko.com/api/v3"
    def __init__(self):
        self.redis_client = RedisService.get_client()
    
    @staticmethod
    def get_price(asset):
        """
        Fetch the price of an asset from CoinGecko.

        Parameters:
        - asset: The asset symbol (e.g., BTC, ETH).

        Returns:
        - The price as a float, or None if not found.
        """
        try:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={asset.lower()}&vs_currencies=usd'
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            if asset.lower() in data:
                return float(data[asset.lower()]['usd'])

            print(f"Warning: {asset} is not available on CoinGecko.")
            return None  # If not found, return None

        except Exception as e:
            print(f"Error fetching price for {asset} from CoinGecko: {e}")
            return None  # No price found

    @staticmethod
    def update_coin_list():
        """Fetch the top 1000 coins from CoinGecko and store them in the database."""
        try:
            db = DatabaseHandler()
            total_coins = 1000  # We want 1000 coins
            coins_per_page = 100  # CoinGecko returns 100 coins per request
            pages = total_coins // coins_per_page  # Number of pages to fetch

            for page in range(1, pages + 1):
                success = False  # Track success of request
                retries = 0  # Retry counter

                while not success and retries < 3:  # Retry up to 3 times
                    try:
                        url = f"{CoinGeckoService.BASE_URL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={coins_per_page}&page={page}"
                        response = requests.get(url)
                        
                        if response.status_code == 429:  # Too Many Requests
                            wait_time = 15  # Wait 15 seconds before retrying
                            print(f"⚠️ Rate limit hit! Waiting {wait_time} seconds before retrying...")
                            time.sleep(wait_time)
                            retries += 1
                            continue  # Retry the request

                        response.raise_for_status()
                        coins = response.json()

                        for coin in coins:
                            symbol = coin["symbol"].upper()
                            coin_id = coin["id"]
                            db.insert_or_update_coin(symbol, coin_id)  # ✅ Save to MySQL

                        success = True  # Mark request as successful
                        time.sleep(3)  # ✅ Prevent hitting rate limits (3-second delay)

                    except requests.exceptions.RequestException as e:
                        print(f"⚠️ Error fetching page {page}: {e}")
                        retries += 1
                        time.sleep(10)  # Wait before retrying

            db.close()
            print("✅ Coin list updated successfully.")

        except Exception as e:
            print(f"⚠️ Error updating CoinGecko coin list: {e}")

    @staticmethod
    def get_historical_prices(symbol: str, days: int = 7):
        """
        Fetch historical price data using CoinGecko ID stored in MySQL.
        If missing, check CoinGecko directly. Cache data in Redis.

        Returns:
        - Historical price data if available.
        - Error message with `symbol` and `coin_id` if an error occurs.
        """
        try:
            if days < 1 or days > 30:
                return {"error": "Days must be between 1 and 30", "symbol": symbol, "coin_id": None}

            redis_client = RedisService.get_client()

            # Check if data is cached in Redis
            cache_key = f"coin_chart:{symbol}:{days}"
            cached_data = redis_client.get(cache_key)

            if cached_data:
                print(f"✅ Serving {symbol} data from Redis cache")
                return json.loads(cached_data)

            # Get CoinGecko ID from MySQL
            db = DatabaseHandler()
            coin_id = db.get_coin_id(symbol)
            db.close()

            # If no CoinGecko ID is found in MySQL, check CoinGecko API
            if not coin_id:
                print(f"⚠️ No CoinGecko ID found for {symbol} in database. Checking CoinGecko API...")
                available, coin_id = CoinGeckoService.is_asset_available(symbol)

                if not available:
                    error_message = f"⚠️ {symbol} is not listed on CoinGecko."
                    return {"error": error_message, "symbol": symbol, "coin_id": None}
                else:
                    print(f"✅ Found {symbol} on CoinGecko with ID: {coin_id}")

            # Call CoinGecko API
            url = f"{CoinGeckoService.BASE_URL}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
            
            retries = 0
            while retries < 3:
                response = requests.get(url)

                if response.status_code == 429:  # Too many requests
                    print("⚠️ Rate limit hit! Retrying in 15 seconds...")
                    time.sleep(15)
                    retries += 1
                    continue  # Retry request
                
                if response.status_code == 404:
                    error_message = f"⚠️ No price data found for symbol: {symbol}, coinID: {coin_id}"
                    return {"error": error_message, "symbol": symbol, "coin_id": coin_id}

                response.raise_for_status()
                data = response.json()

                if "prices" not in data or not data["prices"]:
                    error_message = f"⚠️ No price data available for symbol: {symbol}, coinID: {coin_id}"
                    return {"error": error_message, "symbol": symbol, "coin_id": coin_id}

                # ✅ Cache data in Redis for 5 minutes (300 seconds)
                redis_client.setex(cache_key, 300, json.dumps(data["prices"]))

                return data["prices"]

        except requests.exceptions.RequestException as e:
            error_message = f"⚠️ Error fetching chart data: {str(e)}"
            print(error_message)
            return {"error": error_message, "symbol": symbol, "coin_id": coin_id if 'coin_id' in locals() else None}

        
    @staticmethod
    def is_asset_available(asset):
        """
        Check if an asset is available on CoinGecko by using a cached asset list.
        This list is fetched only once per day.

        Parameters:
        - asset (str): Asset symbol (e.g., 'BTC', 'ETH').

        Returns:
        - (True, coin_id) if available
        - (False, None) if not available or request fails
        """
        try:
            redis_client = RedisService.get_client()
            cache_key = "coingecko_asset_list"

            # ✅ Step 1: Check if the CoinGecko asset list is cached
            cached_assets = redis_client.get(cache_key)
            if cached_assets:
                asset_dict = json.loads(cached_assets)  # Convert JSON string to dictionary
            else:
                # ❗ Step 2: Cache expired or missing → Fetch from CoinGecko
                print("🔄 Fetching new CoinGecko asset list...")
                url = f"{CoinGeckoService.BASE_URL}/coins/list"
                response = requests.get(url)
                response.raise_for_status()

                coins = response.json()
                asset_dict = {coin["symbol"].lower(): coin["id"] for coin in coins}  # Convert to dictionary

                # Cache for 1 day (86,400 seconds)
                redis_client.setex(cache_key, 86400, json.dumps(asset_dict))

            # ✅ Step 3: Check if the asset exists in CoinGecko
            coin_id = asset_dict.get(asset.lower())  # Lookup by lowercase symbol
            return (True, coin_id) if coin_id else (False, None)

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error checking asset availability on CoinGecko: {e}")
            return False, None  # Assume unavailable if API request fails

    def get_all_prices(self):
        """
        Fetches all CoinGecko prices in a single request and caches them.

        Returns:
        - A dictionary of asset prices, e.g., {"bitcoin": 42700, "ethereum": 2950}.
        """
        try:
            # Check Redis cache
            cached_prices = self.redis_client.get("coingecko_prices")
            if cached_prices:
                return json.loads(cached_prices)

            # Fetch prices from CoinGecko
            url = f"{self.BASE_URL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1"
            all_prices = {}
            retries = 0

            while retries < 3:
                response = requests.get(url)
                
                if response.status_code == 429:  # Too many requests
                    wait_time = 2 ** retries  # Exponential backoff
                    print(f"⚠️ Rate limit hit! Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                    continue  # Retry request
                
                response.raise_for_status()
                prices = response.json()

                # Convert to dictionary { "bitcoin": 32000, "ethereum": 2200, ... }
                all_prices = {item["id"]: float(item["current_price"]) for item in prices}

                # Cache for 60 seconds
                self.redis_client.setex("coingecko_prices", 60, json.dumps(all_prices))

                return all_prices

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching bulk prices from CoinGecko: {e}")
            return {}