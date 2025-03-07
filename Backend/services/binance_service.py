from datetime import datetime,timedelta
from binance.spot import Spot as Client
import requests
from services.redis_service import RedisService
import json
from services.coingecko_service import CoinGeckoService
from db.db_handler import DatabaseHandler
import asyncio
import aiohttp
from collections import defaultdict
UNSUPPORTED_ASSETS = set()
import urllib.parse
import time
import hmac
import hashlib
from concurrent.futures import ThreadPoolExecutor

class BinanceService:
    def __init__(self, api_key=None, api_secret=None):
        # self.client = Client(api_key, api_secret)
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(api_key, api_secret) if api_key and api_secret else None
        self.redis_client = RedisService.get_client()
        self.DatabaseHandler = DatabaseHandler()


    def _convert_to_datetime(dt):
        """Helper: Convert dt to datetime if it's a string."""
        if isinstance(dt, str):
            return datetime.strptime(dt, "%Y-%m-%d")
        return dt

    @staticmethod
    def convert_timestamp(raw_timestamp):
        """
        Converts a Binance timestamp (milliseconds) into a MySQL-compatible datetime format.

        Parameters:
        - raw_timestamp: The timestamp from Binance (int, string, or preformatted).

        Returns:
        - A formatted timestamp (YYYY-MM-DD HH:MM:SS) or None if invalid.
        """
        try:
            print(f"🟡 Raw timestamp received: {raw_timestamp}")  # Debugging

            if not raw_timestamp:
                print(f"❌ Skipping conversion: raw_timestamp is None or empty")
                return None  

            # ✅ If it's already in the correct format, return it
            if isinstance(raw_timestamp, str):
                try:
                    # Check if it matches the expected format
                    parsed_time = datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S")
                    print(f"✅ Timestamp already in correct format: {parsed_time}")
                    return raw_timestamp
                except ValueError:
                    pass  # Not in expected format, continue to other checks

            # ✅ If it's an integer (milliseconds), convert it
            if isinstance(raw_timestamp, int) or (isinstance(raw_timestamp, str) and raw_timestamp.isdigit()):
                converted_time = datetime.utcfromtimestamp(int(raw_timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                print(f"✅ Converted timestamp (int/ms): {converted_time}")
                return converted_time

        except Exception as e:
            print(f"❌ Error converting timestamp: {raw_timestamp} - {e}")
            return None  

        print(f"❌ Skipping conversion for timestamp: {raw_timestamp}")
        return None
    
    @staticmethod
    def convert_to_timestamp(date_input):
        """Convert a date (string or datetime) to a Binance-compatible timestamp in milliseconds."""
        if isinstance(date_input, datetime):
            return int(date_input.timestamp() * 1000)  # Convert to milliseconds
        elif isinstance(date_input, str):
            try:
                return int(datetime.strptime(date_input, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            except ValueError:  # If format doesn't match, try without time
                return int(datetime.strptime(date_input, "%Y-%m-%d").timestamp() * 1000)
        return None  # Return None if the input is invalid

    
    # @staticmethod
    # def convert_to_timestamp(date_str):
    #     """Convert a date string (YYYY-MM-DD) to a Binance-compatible timestamp in milliseconds."""
    #     if date_str:
    #         return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp() * 1000)  # Convert to milliseconds
    #     return None
    
    # def get_account_snapshot(self):
    #     try:
    #         return self.client.account_snapshot("SPOT")
    #     except Exception as e:
    #         print(f"Error fetching account snapshot: {e}")
    #         return {}
    def get_account_snapshot(self):
            cache_key = "binance:account_snapshot"
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                return json.loads(cached_data)  # ✅ Return cached data if available

            response = self.client.account_snapshot(type="SPOT")

            # ✅ Cache the result in Redis for 60 seconds
            self.redis_client.setex(cache_key, 60, json.dumps(response))

            return response

    def get_trade_history(self, symbol):
        try:
            return self.client.my_trades(symbol=symbol)
        except Exception as e:
            print(f"Error fetching trade history for {symbol}: {e}")
            return []

    def get_all_prev_close_prices(self):
        """
        Fetches the previous close prices for all USDT trading pairs from Binance in a single request and caches them.
        
        Returns:
        - A dictionary of previous close prices, e.g., {"BTC": 32000, "ETH": 2200, ...}
        """
        try:
            # Check Redis cache
            cached_prices = self.redis_client.get("binance_prev_close_prices")
            if cached_prices:
                return json.loads(cached_prices)

            # Fetch from Binance API (24hr ticker endpoint)
            url = 'https://api.binance.com/api/v3/ticker/24hr'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Build dictionary for assets ending with 'USDT'
            price_dict = {
                item["symbol"].replace("USDT", ""): float(item["prevClosePrice"])
                for item in data if item["symbol"].endswith("USDT")
            }

            # Cache for 60 seconds
            self.redis_client.setex("binance_prev_close_prices", 60, json.dumps(price_dict))

            return price_dict
        except Exception as e:
            print(f"Error fetching bulk previous close prices from Binance: {e}")
            return {}

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


        def fetch_crypto_transactions_for_period(self, user_id, start_date, end_date):
            """
        Fetch Binance deposits & withdrawals in **90-day chunks** and store them sequentially.
        """
        start_time = self.convert_to_timestamp(start_date)
        end_time = self.convert_to_timestamp(end_date)

        current_time = start_time
        chunk_size = 90 * 24 * 60 * 60 * 1000  # 90 days in milliseconds
        total_deposits, total_withdrawals = 0, 0

        while current_time < end_time:
            next_time = min(current_time + chunk_size, end_time)

            # ✅ Fetch & Store Deposits
            deposits = self.fetch_crypto_deposits_for_period(current_time, next_time)
            self.store_transactions(user_id, deposits, "Deposit")
            total_deposits += len(deposits)

            # ✅ Fetch & Store Withdrawals
            withdrawals = self.fetch_crypto_withdrawals_for_period(current_time, next_time)
            self.store_transactions(user_id, withdrawals, "Withdrawal")
            total_withdrawals += len(withdrawals)

            print(f"🔹 Processed {datetime.fromtimestamp(current_time/1000)} - {datetime.fromtimestamp(next_time/1000)}")
            current_time = next_time  # Move to next 90-day chunk

        return {"deposits_fetched": total_deposits, "withdrawals_fetched": total_withdrawals}

    def fetch_crypto_transactions_for_period(self, user_id, start_date, end_date):
        """
        Fetch Binance deposits & withdrawals **in 90-day chunks** and store them sequentially.
        ✅ Keeps original structure with user_id & db_handler.
        """
        start_time = self.convert_to_timestamp(start_date)
        end_time = self.convert_to_timestamp(end_date)

        if not start_time or not end_time:
            print("❌ Invalid date format provided.")
            return {"error": "Invalid date format"}

        current_time = start_time
        chunk_size = 90 * 24 * 60 * 60 * 1000  # 90 days in milliseconds
        total_deposits, total_withdrawals = 0, 0

        while current_time < end_time:
            next_time = min(current_time + chunk_size, end_time)

            # ✅ Fetch & Store Deposits
            deposits = self.fetch_crypto_deposits_for_period(current_time, next_time)
            self.store_transactions(user_id, deposits, "DEPOSIT")
            total_deposits += len(deposits)

            # ✅ Fetch & Store Withdrawals
            withdrawals = self.fetch_crypto_withdrawals_for_period(current_time, next_time)
            self.store_transactions(user_id, withdrawals, "WITHDRAW")
            total_withdrawals += len(withdrawals)

            print(f"✅ Processed {datetime.fromtimestamp(current_time/1000)} to {datetime.fromtimestamp(next_time/1000)}")
            current_time = next_time  # Move to next 90-day chunk

        return {"deposits_fetched": total_deposits, "withdrawals_fetched": total_withdrawals}

    def fetch_crypto_deposits_for_period(self, start_time, end_time):
        """Fetch Binance deposits within a **valid** 90-day range."""
        try:
            response = self.client.deposit_history(startTime=start_time, endTime=end_time, limit=1000)
            print(f"🔹 Binance Deposits Response: {response}")
            return response if response else []
        except Exception as e:
            print(f"❌ Error fetching deposits: {e}")
            return []

    def fetch_crypto_withdrawals_for_period(self, start_time, end_time):
        """Fetch Binance withdrawals within a **valid** 90-day range."""
        try:
            response = self.client.withdraw_history(startTime=start_time, endTime=end_time, limit=1000)
            print(f"🔹 Binance Withdrawals Response: {response}")
            return response if response else []
        except Exception as e:
            print(f"❌ Error fetching withdrawals: {e}")
            return []

    def store_transactions(self, user_id, transactions, txn_type):
        """Store transactions (Deposits or Withdrawals) in the database."""
        for txn in transactions:
            try:
                asset_name = txn.get("coin")
                amount = float(txn.get("amount"))
                # ✅ Get timestamp (either `insertTime` for Deposits or `applyTime` for Withdrawals)
                timestamp_raw = txn.get("insertTime") if txn_type == "DEPOSIT" else txn.get("applyTime")

                # ✅ Convert to human-readable string format (YYYY-MM-DD HH:MM:SS)
                if isinstance(timestamp_raw, str):
                    # Convert from `YYYY-MM-DD HH:MM:SS` to proper format
                    timestamp = datetime.strptime(timestamp_raw, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # Convert from milliseconds to proper format
                    timestamp = datetime.fromtimestamp(timestamp_raw / 1000).strftime("%Y-%m-%d %H:%M:%S")

                # ✅ Store in database as VARCHAR (string)
                username = self.DatabaseHandler.get_username_by_user_id(user_id=user_id)
                self.DatabaseHandler.insert_transaction_if_not_exists(username, asset_name, timestamp, amount, 0, txn_type, 0)
                print(f"🟢 {txn_type} stored: {asset_name}, Amount: {amount}, Time: {timestamp}")

            except Exception as e:
                print(f"❌ Error storing {txn_type}: {e} - Data: {txn}")




    def get_fiat_transactions(self, user_id, start_time=None, end_time=None):
        """
        Fetches both fiat deposits and withdrawals from Binance for all fiat currencies.

        Returns:
        A dictionary containing total deposits and withdrawals for each fiat currency.
        """
        db_handler = DatabaseHandler()
        username = db_handler.get_username_by_user_id(user_id)

        deposits_total = self.get_fiat_deposits(db_handler, user_id, username, start_time, end_time)
        withdrawals_total = self.get_fiat_withdrawals(db_handler, user_id, username, start_time, end_time)

        return {
            "total_deposits": deposits_total,
            "total_withdrawals": withdrawals_total
        }

    def get_fiat_deposits(self, db_handler, user_ID, username, start_time=None, end_time=None):
        """
        Fetch all fiat deposits from Binance and insert them into the database if they don't exist.
        
        Returns:
        A dictionary containing the total amount of deposits for each fiat currency.
        """
        deposits = defaultdict(float)
        page = 1
        rows_per_page = 500
        start_time = BinanceService.convert_to_timestamp(start_time)
        end_time = BinanceService.convert_to_timestamp(end_time)

        while True:
            response = self.client.fiat_order_history(
                transactionType='0',  # '0' for deposit
                beginTime=start_time,
                endTime=end_time,
                page=page,
                rows=rows_per_page
            )

            if response['code'] != '000000':
                print(f"Error fetching deposits: {response['message']}")
                break

            # Process deposits
            for deposit in response['data']:
                if deposit.get('status') in ['Successful', 'Finished']:
                    fiat_currency = deposit.get('fiatCurrency', 'UNKNOWN')
                    amount = float(deposit.get('amount', 0))
                    timestamp = deposit.get('createTime')

                    if timestamp:
                        timestamp = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                    # Insert into database
                    db_handler.insert_transaction_if_not_exists(username, fiat_currency, timestamp, amount, 1, "DEPOSIT", 0)

                    # Aggregate total deposits
                    deposits[fiat_currency] += amount

            # Stop if fewer than the max rows were returned
            if len(response['data']) < rows_per_page:
                break
            page += 1

        return dict(deposits)

    def get_fiat_withdrawals(self, db_handler, user_ID, username, start_time=None, end_time=None):
        """
        Fetch all fiat withdrawals from Binance and insert them into the database if they don't exist.
        
        Returns:
        A dictionary containing the total amount of withdrawals for each fiat currency.
        """
        withdrawals = defaultdict(float)
        page = 1
        rows_per_page = 500
        start_time = BinanceService.convert_to_timestamp(start_time)
        end_time = BinanceService.convert_to_timestamp(end_time)

        while True:
            response = self.client.fiat_order_history(
                transactionType='1',  # '1' for withdrawal
                beginTime=start_time,
                endTime=end_time,
                page=page,
                rows=rows_per_page
            )

            if response['code'] != '000000':
                print(f"Error fetching withdrawals: {response['message']}")
                break

            # Process withdrawals
            for withdrawal in response['data']:
                if withdrawal.get('status') in ['Successful', 'Finished']:
                    fiat_currency = withdrawal.get('fiatCurrency', 'UNKNOWN')
                    amount = float(withdrawal.get('amount', 0))
                    timestamp = withdrawal.get('createTime')

                    if timestamp:
                        timestamp = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                    # Insert into database
                    db_handler.insert_transaction_if_not_exists(username, fiat_currency, timestamp, amount, 1, "WITHDRAW", 0)

                    # Aggregate total withdrawals
                    withdrawals[fiat_currency] += amount

            # Stop if fewer than the max rows were returned
            if len(response['data']) < rows_per_page:
                break
            page += 1

        return dict(withdrawals)

    @staticmethod
    def store_binance_transactions(db_handler, user_id: int, transactions, transaction_type):
        """
        Store Binance withdrawals or deposits in the database.
        If an asset is not found, it is automatically added or updated.

        Parameters:
        - db_handler: Database handler instance.
        - user_id: ID of the user making the transactions.
        - transactions: List of transactions from Binance API.
        - transaction_type: Either 'WITHDRAW' or 'DEPOSIT'.
        """
        for tx in transactions:
            asset_name = tx.get("coin")  # Asset symbol (e.g., BTC, ETH)
            amount = float(tx.get("amount", 0))
            timestamp = BinanceService.convert_timestamp(tx.get("insertTime") or tx.get("applyTime"))

            if not timestamp:
                print(f"⚠️ Skipping transaction {tx.get('txId')} due to invalid timestamp ({tx.get('insertTime')})")
                continue

            # 🔹 Use insert_or_update_asset() to ensure the asset exists in the database
            avg_price = 0  # Deposits & withdrawals typically don't have a price
            db_handler.insert_or_update_asset(user_id, asset_name, amount, avg_price)

            # Fetch the AssetID after ensuring it exists
            asset_id = db_handler.get_asset_id(asset_name)
            username = db_handler.get_username_by_user_id(user_id)

            if not asset_id:
                print(f"⚠️ Skipping transaction {tx.get('txId')} - Failed to retrieve asset {asset_name}.")
                continue

            # 🔹 Check if the transaction already exists before inserting
            if db_handler.transaction_exists(asset_name, user_id, timestamp, amount):
                print(f"🔄 Transaction already exists: {tx.get('txId')} - Skipping duplicate entry.")
                continue

            # 🔹 Insert the transaction into the database
            try:
                db_handler.insert_transaction_if_not_exists(
                    asset_name=asset_name,
                    username=username,
                    time=timestamp,
                    quantity=amount,
                    price=0,  # Withdrawals & deposits usually don't have a price
                    action=transaction_type,
                    commission=0  # Default commission to 0
                )
                print(f"✅ Stored {transaction_type} transaction for {asset_name}: {amount} units")
            except Exception as e:
                print(f"❌ Error storing {transaction_type} transaction: {e}")

    #Parallel
    @staticmethod
    def get_asset_daily_balance(asset: str, amount: float, days: int):
        """
        Retrieve daily candlestick data for the given asset over the past `days` days using Binance's API,
        and compute the daily USD value by multiplying the closing price by the given amount.
        
        Returns:
            A dictionary mapping each date (YYYY-MM-DD) to the asset's USD value.
        """
        # Get daily prices: returns a list of [timestamp, close_price] pairs.
        daily_prices = BinanceService.get_daily_prices(asset, days=days)
        asset_daily_balance = {}
        for data_point in daily_prices:
            timestamp = data_point[0]  # Timestamp in milliseconds.
            date_str = datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
            close_price = data_point[1]
            asset_daily_balance[date_str] = amount * close_price
        return asset_daily_balance

    @staticmethod
    def is_asset_available(asset):
        """
        Check if an asset is available on Binance by using a cached list of trading pairs.
        This list is fetched only once per day.

        Parameters:
        - asset (str): Asset symbol (e.g., 'BTC', 'ETH').

        Returns:
        - True if available, False otherwise.
        """
        try:
            redis_client = RedisService.get_client()
            cache_key = "binance_trading_pairs"

            # ✅ Step 1: Check if Binance pairs are cached in Redis
            cached_pairs = redis_client.get(cache_key)
            if cached_pairs:
                binance_symbols = set(json.loads(cached_pairs))  # Convert cached list to set
            else:
                # ❗ Step 2: Cache expired or missing → Fetch from Binance
                print("🔄 Fetching new Binance trading pairs...")
                url = "https://api.binance.com/api/v3/exchangeInfo"
                response = requests.get(url)
                response.raise_for_status()

                symbols = {s["symbol"] for s in response.json()["symbols"]}  # Convert list to set
                redis_client.setex(cache_key, 86400, json.dumps(list(symbols)))  # Cache for 1 day (86,400 sec)
                binance_symbols = symbols

            # ✅ Step 3: Check if the asset exists in Binance
            return f"{asset.upper()}USDT" in binance_symbols  # Binance pairs are uppercase

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error checking asset availability on Binance: {e}")
            return False  # Assume unavailable if API request fails

    @staticmethod
    async def _fetch_daily_prices_for_asset(asset: str, days: int, semaphore: asyncio.Semaphore):
        """
        Asynchronously fetch daily candlestick data for a given asset (e.g., BTC) using Binance's API.
        Returns a tuple: (asset, list of [timestamp, close_price] pairs).
        """
        symbol = f"{asset.upper()}USDT"
        # Check if the asset is available on Binance.
        if not BinanceService.is_asset_available(asset):
            print(f"Asset {asset} not available on Binance.")
            return asset, []
        
        interval = "1d"
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": int(start_time.timestamp() * 1000),
            "endTime": int(end_time.timestamp() * 1000),
            "limit": days
        }
        url = "https://api.binance.com/api/v3/klines"
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, params=params) as response:
                        response.raise_for_status()
                        data = await response.json()
                        daily_prices = []
                        for candle in data:
                            # candle format: [Open time, Open, High, Low, Close, ...]
                            timestamp = candle[0]
                            close_price = float(candle[4])
                            daily_prices.append([timestamp, close_price])
                        return asset, daily_prices
                except Exception as e:
                    print(f"Error fetching daily prices for {asset}: {e}")
                    return asset, []

    @staticmethod
    async def get_daily_prices_for_assets_parallel(assets: list, days: int, max_concurrent: int = 10):
        """
        Asynchronously fetch daily prices for a list of asset symbols concurrently.
        :param assets: List of asset symbols (e.g., ["BTC", "ETH", ...]).
        :param days: Number of days for which to fetch data.
        :param max_concurrent: Maximum number of concurrent requests.
        :return: Dictionary mapping asset symbol to its list of [timestamp, close_price] pairs.
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []
        for asset in assets:
            tasks.append(BinanceService._fetch_daily_prices_for_asset(asset, days, semaphore))
        results = await asyncio.gather(*tasks)
        return {asset: prices for asset, prices in results}

    @staticmethod
    def get_assets_daily_balances_parallel(assets_with_amount: list, days: int, max_concurrent: int = 10):
        """
        Synchronous wrapper that takes a list of tuples (asset, amount), fetches daily prices in parallel,
        calculates the daily USD value (amount * closing price) for each asset, and aggregates the results.
        :param assets_with_amount: List of tuples, e.g., [("BTC", 0.5), ("ETH", 2.0), ...].
        :param days: Number of days for which to fetch daily prices.
        :param max_concurrent: Maximum number of concurrent requests.
        :return: Dictionary mapping date (YYYY-MM-DD) to aggregated USD value.
        """
        # Extract asset symbols.
        asset_symbols = [asset for asset, _ in assets_with_amount]
        # Run the asynchronous function to fetch prices concurrently.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        prices_dict = loop.run_until_complete(
            BinanceService.get_daily_prices_for_assets_parallel(asset_symbols, days, max_concurrent)
        )
        loop.close()
        # Aggregate daily USD values.
        total_daily_balance = {}
        for asset, amount in assets_with_amount:
            daily_prices = prices_dict.get(asset, [])
            for data_point in daily_prices:
                timestamp = data_point[0]
                date_str = datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
                close_price = data_point[1]
                usd_value = amount * close_price
                total_daily_balance[date_str] = total_daily_balance.get(date_str, 0) + usd_value
        return total_daily_balance