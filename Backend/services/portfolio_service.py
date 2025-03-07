from services.redis_service import RedisService
from services.binance_service import BinanceService
from db.db_handler import DatabaseHandler
import pandas as pd
import numpy as np
import json
from services.coingecko_service import CoinGeckoService
import logging
from datetime import datetime, timedelta
logging.basicConfig(level=logging.INFO)
import asyncio

class PortfolioService:
    @staticmethod
    def sync_portfolio(user_id, api_key, api_secret):
        db = DatabaseHandler()
        binance = BinanceService(api_key, api_secret)

        try:
            # Fetch portfolio data from Binance
            snapshot = binance.get_account_snapshot()
            for snapshot_entry in snapshot.get("snapshotVos", []):
                for balance in snapshot_entry["data"]["balances"]:
                    asset_name = balance["asset"]
                    free_amount = float(balance["free"])
                    locked_amount = float(balance["locked"])
                    total_amount = free_amount + locked_amount
                    if asset_name in ["USDT", "NFT","USDC","EUR","USD"]:
                        continue
                    logging.info(f"Asset: {asset_name}, Total: {total_amount}")

                    if total_amount > 0:
                        # Fetch the current price of the asset
                        # price = binance.get_coin_price(asset_name)
                        avg_price = binance.check_average_price(asset_name)
                        logging.info(f"avg_price: {avg_price}")
                        if avg_price is None or avg_price == 0:
                            print(f"⚠ Warning: {asset_name} has no trade history. Setting avg_price to 0.")
                            avg_price = 0  # Default to zero if no trade history is available

                        # Insert or update the asset in the database
                        db.insert_or_update_asset(
                            user_id=user_id,
                            asset_name=asset_name,
                            amount=total_amount,
                            avg_price=avg_price,
                            )
        except Exception as e:
            print(f"Error syncing portfolio for user {user_id}: {e}")
        finally:
            db.close()

    @staticmethod
    def fetch_portfolio_daily_performance(user_id):
        

        """
        Fetch portfolio performance by retrieving asset data from the database,
        fetching real-time prices from Binance, and calculating gain/loss percentage.

        Parameters:
        - user_id: The ID of the user.
        - api_key: Binance API key.
        - api_secret: Binance API secret.

        Returns:
        - A list of dictionaries containing asset performance data.
        """
        db = DatabaseHandler()

        try:
            # Fetch asset data from the database
            df_avg_prices = db.get_user_assets(user_id)

            if df_avg_prices.empty:
                return {"message": "No assets found for this user."}

            # Fetch current and previous prices using BinanceService
            df_avg_prices['Today_Price'] = df_avg_prices['Asset'].apply(BinanceService.get_coin_price)
            df_avg_prices['Yesterday_Price'] = df_avg_prices['Asset'].apply(lambda x: BinanceService.get_coin_price(x, "yesterday"))

            # Calculate Gain/Loss Percentage
            df_avg_prices['Gain_Loss_Percentage'] = (
                (df_avg_prices['Today_Price'] - df_avg_prices['Average_Price']) / df_avg_prices['Average_Price'] * 100
            ).replace([np.inf, -np.inf], np.nan).fillna('Free')

            # Convert DataFrame to a list of dictionaries for JSON response
            return df_avg_prices.to_dict(orient="records")

        except Exception as e:
            return {"error": f"Error fetching portfolio daily performance: {e}"}
        finally:
            db.close()

    # @staticmethod
    # def get_user_assets(user_id):
    #     """
    #     Fetches user assets from the database.

    #     Parameters:
    #     - user_id: The ID of the user.

    #     Returns:
    #     - A list of user assets containing:
    #         - Asset (Symbol)
    #         - Average_Price (User’s recorded price)
    #         - Amount (Total held)
    #         - Today_Price (Current price from Binance)
    #         - Total_Value (Value of this asset in USD)
    #         - Portfolio_Percentage (Percentage of total portfolio)
    #     """
    #     db = DatabaseHandler()
    #     binance = BinanceService()

    #     try:
    #         df_assets = db.get_user_assets(user_id)

    #         if df_assets.empty:
    #             return {"message": "No assets found for this user."}

    #         # Fetch all Binance prices at once
    #         prices = binance.get_all_prices()

    #         # Assign prices to each asset, ensuring missing prices get `0`
    #         df_assets['Today_Price'] = df_assets['Asset'].apply(lambda x: prices.get(x, 0))

    #         # Ensure Average_Price is not NULL
    #         df_assets['Average_Price'].fillna(0, inplace=True)

    #         # Calculate total value of each asset
    #         df_assets['Total_Value'] = df_assets['Today_Price'] * df_assets['Amount']

    #         # Calculate total portfolio value
    #         total_portfolio_value = df_assets['Total_Value'].sum()

    #         # **Fix: Avoid division by zero**
    #         if total_portfolio_value > 0:
    #             df_assets['Portfolio_Percentage'] = (df_assets['Total_Value'] / total_portfolio_value * 100).round(2)
    #         else:
    #             df_assets['Portfolio_Percentage'] = 0  # Avoid division by zero

    #         # Convert DataFrame to JSON format
    #         return df_assets.to_dict(orient="records")


    #     except Exception as e:
    #         print(f"Error fetching user assets: {e}")
    #         return {"error": f"Error fetching user assets: {e}"}
    #     finally:
    #         db.close()


    @staticmethod
    def get_user_assets(user_id):
        """
        Fetches user assets from the database while ensuring they exist on Binance or CoinGecko.

        Parameters:
        - user_id: The ID of the user.

        Returns:
        - A list of user assets containing:
            - Asset (Symbol)
            - Average_Price (User’s recorded price)
            - Amount (Total held)
            - Today_Price (Current price from Binance or CoinGecko)
            - Total_Value (Value of this asset in USD)
            - Portfolio_Percentage (Percentage of total portfolio)
        """
        db = DatabaseHandler()
        binance = BinanceService()
        Coingecko = CoinGeckoService()

        try:
            df_assets = db.get_user_assets(user_id)

            if df_assets.empty:
                return {"message": "No assets found for this user."}

            # Remove assets that are unavailable on both Binance and CoinGecko
            valid_assets = [
                asset for asset in df_assets['Asset']
                if BinanceService.is_asset_available(asset) or CoinGeckoService.is_asset_available(asset)
            ]

            if not valid_assets:
                return {"message": "No valid assets found for this user."}

            # Fetch all Binance & CoinGecko prices
            prices = binance.get_all_prices()
            coingecko_prices = Coingecko.get_all_prices()

            # Merge Binance & CoinGecko prices automatically
            for asset in df_assets['Asset']:
                if asset not in prices:  # Use CoinGecko only if missing in Binance
                    prices[asset] = coingecko_prices.get(asset, 0)
            # Assign prices, ensuring missing ones get `0`
            df_assets['Today_Price'] = df_assets['Asset'].apply(lambda x: prices.get(x, 0))

            # Ensure Average_Price is not NULL
            # df_assets['Average_Price'].fillna(0, inplace=True)
            df_assets['Average_Price'] = df_assets['Average_Price'].fillna(0)

            # Calculate total value of each asset
            df_assets['Total_Value'] = df_assets['Today_Price'] * df_assets['Amount']

            # Calculate total portfolio value
            total_portfolio_value = df_assets['Total_Value'].sum()

            # **Fix: Avoid division by zero**
            if total_portfolio_value > 0:
                df_assets['Portfolio_Percentage'] = (df_assets['Total_Value'] / total_portfolio_value * 100).round(2)
            else:
                df_assets['Portfolio_Percentage'] = 0  # Avoid division by zero

            # Convert DataFrame to JSON format
            return df_assets.to_dict(orient="records")

        except Exception as e:
            print(f"Error fetching user assets: {e}")
            return {"error": f"Error fetching user assets: {e}"}
        finally:
            db.close()

    @staticmethod
    def set_average_price(user_id, asset_name, avg_price, amount=None):
        """
        Sets the average price for a specific asset for a specific user.
        If the asset exists, it updates only the average price.
        If the asset does not exist, it inserts a new record (amount is required).

        Parameters:
        - user_id: The ID of the user.
        - asset_name: The asset symbol (e.g., BTC).
        - avg_price: The new average price to set.
        - amount: Optional. If updating, we keep the existing amount.

        Returns:
        - A success message or error.
        """
        db = DatabaseHandler()

        try:
            # Check if asset exists
            query_check = "SELECT Amount FROM Asset WHERE Name = %s AND UserID = %s"
            db.cursor.execute(query_check, (asset_name, user_id))
            existing_asset = db.cursor.fetchone()

            if existing_asset:
                # **If asset exists, keep the current amount if amount is not provided**
                existing_amount = existing_asset[0]
                amount = amount if amount is not None else existing_amount

            else:
                # **If asset does NOT exist, amount is required**
                if amount is None:
                    return {"error": "Amount is required when adding a new asset."}

            # Insert or update the asset
            db.insert_or_update_asset(user_id, asset_name, amount, avg_price)

            return {"message": f"Average price for {asset_name} updated successfully for user {user_id}."}

        except Exception as e:
            return {"error": f"Error setting average price: {e}"}
        finally:
            db.close()

    @staticmethod
    def get_assets_with_zero_avg_price(user_id):
        """
        Fetch all assets for a specific user where Average_Price = 0.

        Parameters:
        - user_id: The ID of the user.

        Returns:
        - A list of assets where Average_Price = 0.
        """
        db = DatabaseHandler()

        try:
            assets = db.get_assets_with_zero_average_price(user_id)
            if not assets:
                return {"message": "No assets found with zero average price."}
            return {"assets": assets}
        except Exception as e:
            return {"error": f"Error fetching assets with zero average price: {e}"}
        finally:
            db.close()

    @staticmethod
    def get_daily_performance(user_id):
        """
        Fetch daily performance for a user by:
        - Retrieving user assets from the database.
        - Using cached bulk Binance data for today's and yesterday's prices.
        - Calculating gain/loss, total value, daily change, and determining best/worst performers.
        - Caching the result in Redis.
        """
        redis_client = RedisService.get_client()
        cache_key = f"daily_performance:user:{user_id}"

        # ✅ Check Redis cache first
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logging.info("✅ Using cached data from Redis")
            return json.loads(cached_data)

        db = DatabaseHandler()
        binance = BinanceService()  # Assumes BinanceService includes get_all_prices and get_all_prev_close_prices

        try:
            # ✅ Fetch user assets from the database (returns a DataFrame)
            df_assets = db.get_user_assets(user_id)
            if df_assets.empty:
                return {"message": "No assets found for this user."}

            # ✅ Fetch bulk prices from Binance
            current_prices = binance.get_all_prices()  # e.g., {"BTC": 32000, "ETH": 2200, ...}
            prev_close_prices = binance.get_all_prev_close_prices()  # e.g., {"BTC": 31500, "ETH": 2180, ...}

            # ✅ Update DataFrame with today's and yesterday's prices using batch data
            df_assets['Today_Price'] = df_assets['Asset'].apply(lambda asset: current_prices.get(asset.upper()))
            df_assets['Yesterday_Price'] = df_assets['Asset'].apply(lambda asset: prev_close_prices.get(asset.upper()))

            # ✅ Calculate Gain/Loss Percentage per asset
            df_assets['Gain_Loss_Percentage'] = (
                (df_assets['Today_Price'] - df_assets['Yesterday_Price']) / df_assets['Yesterday_Price'] * 100
            ).replace([np.inf, -np.inf], np.nan).fillna(0)

            # ✅ Calculate Total Value per asset and overall balance
            df_assets['Total_Value'] = df_assets['Today_Price'] * df_assets['Amount']
            total_balance = df_assets['Total_Value'].sum()

            # ✅ Calculate Daily Change and Daily PnL
            df_assets['Daily_Change'] = (df_assets['Today_Price'] - df_assets['Yesterday_Price']) * df_assets['Amount']
            daily_pnl = df_assets['Daily_Change'].sum()

            # ✅ Determine Best and Worst Performers (only for assets with Total_Value > $10)
            df_filtered = df_assets[df_assets['Total_Value'] > 10]
            if df_filtered.empty or len(df_filtered) < 2:
                best_performer = worst_performer = {"message": "No significant assets found (>$10)."}
            else:
                best_performer = df_filtered.loc[df_filtered['Gain_Loss_Percentage'].idxmax(), 
                                                ['Asset', 'Gain_Loss_Percentage', 'Total_Value']].to_dict()
                worst_performer = df_filtered.loc[df_filtered['Gain_Loss_Percentage'].idxmin(), 
                                                    ['Asset', 'Gain_Loss_Percentage', 'Total_Value']].to_dict()
                best_performer['Portfolio_Percentage'] = round((best_performer['Total_Value'] / total_balance) * 100, 2)
                worst_performer['Portfolio_Percentage'] = round((worst_performer['Total_Value'] / total_balance) * 100, 2)
                best_performer["Total_Value"] = round(best_performer["Total_Value"], 2)
                worst_performer["Total_Value"] = round(worst_performer["Total_Value"], 2)

            result = {
                "total_balance": round(total_balance, 2),
                "daily_pnl": round(daily_pnl, 2),
                "best_performer": best_performer,
                "worst_performer": worst_performer
            }

            # ✅ Cache the result in Redis (expires in 1 hour)
            redis_client.setex(cache_key, 3600, json.dumps(result))

            return result

        except Exception as e:
            return {"error": f"Error fetching daily performance: {e}"}
        finally:
            db.close()


    @staticmethod
    def get_historical_prices(asset: str, days: int = 7):
        """
        Fetch historical price data for an asset using CoinGeckoService.

        Parameters:
        - asset: The asset symbol (e.g., BTC, ETH).
        - days: Number of days for historical data (1 to 30).

        Returns:
        - List of [timestamp, price] pairs, or None if request fails.
        """
        return CoinGeckoService.get_historical_prices(asset, days)

    @staticmethod
    def get_period_balance_with_history(user_id: int, days: int):
        """
        Reconstruct the historical portfolio balance using BUY and SELL transactions.
        Assumes:
          - BUY adds to holdings.
          - SELL subtracts from holdings.
        """
        redis_client = RedisService.get_client()
        cache_key = f"period_balance_history:user:{user_id}:days:{days}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        db = DatabaseHandler()
        # Fetch BUY and SELL transactions
        buys = db.get_all_user_transactions(user_id, "BUY")
        sells = db.get_all_user_transactions(user_id, "SELL")
        db.close()
        
        all_transactions = buys + sells
        if not all_transactions:
            return {"message": "No transactions found for this user."}
        
        # Convert to DataFrame and ensure numeric type for quantity
        df_tx = pd.DataFrame(all_transactions)
        df_tx['Time'] = pd.to_datetime(df_tx['time'])
        df_tx['quantity'] = pd.to_numeric(df_tx['quantity'], errors='coerce')
        
        # Map actions to signed quantities:
        # BUY -> positive, SELL -> negative.
        df_tx['SignedQuantity'] = df_tx.apply(
            lambda row: row['quantity'] if row['action'].upper() == "BUY" 
                        else -row['quantity'], axis=1
        )
        # **Important:** Sort transactions in ascending order!
        df_tx.sort_values('Time', ascending=True, inplace=True)
        
        # Define the period (daily)
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days - 1)
        date_range = pd.date_range(start=start_date, end=end_date)
        
        # Compute cumulative holdings per asset
        assets = df_tx['asset'].unique()
        asset_holdings = {}
        for asset in assets:
            df_asset = df_tx[df_tx['asset'] == asset].copy()
            df_asset.set_index('Time', inplace=True)
            # Calculate cumulative sum in correct order
            df_asset['Cumulative'] = df_asset['SignedQuantity'].cumsum()
            # Resample to daily frequency (take last known value per day)
            daily_holdings = df_asset['Cumulative'].resample('D').last().ffill().fillna(0)
            asset_holdings[asset] = daily_holdings
            # Debug: Log the last few daily holdings for each asset.
        for asset, series in asset_holdings.items():
            print(f"{asset} holdings (last 5 days):")
            print(series.tail(5))
        
        # Fetch daily prices for all assets in parallel using Binance
        assets_list = list(assets)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        prices_dict = loop.run_until_complete(
            BinanceService.get_daily_prices_for_assets_parallel(assets_list, days, max_concurrent=10)
        )
        loop.close()
        
        # Convert price data to pandas Series (indexed by date)
        asset_prices = {}
        for asset, prices_list in prices_dict.items():
            if not prices_list:
                continue
            dates = [datetime.utcfromtimestamp(item[0] / 1000).date() for item in prices_list]
            prices = [item[1] for item in prices_list]
            series = pd.Series(data=prices, index=pd.to_datetime(dates))
            asset_prices[asset] = series
        
        # Compute portfolio value for each day
        portfolio_values = {}
        for single_date in date_range:
            total_value = 0
            for asset in assets:
                holding_series = asset_holdings.get(asset)
                if holding_series is None:
                    continue
                holding = holding_series.get(single_date, 0)
                price_series = asset_prices.get(asset)
                if price_series is None:
                    continue
                # Use the price for the day, or the last available price
                price = price_series.get(single_date)
                if price is None:
                    price = price_series.asof(single_date)
                if pd.isna(price):
                    price = 0
                total_value += holding * price
            portfolio_values[single_date.strftime("%Y-%m-%d")] = total_value
        
        result = [
            {"date": date, "total_balance": round(portfolio_values[date], 2)}
            for date in sorted(portfolio_values.keys())
        ]
        
        redis_client.setex(cache_key, 3600, json.dumps(result))
        return result

    @staticmethod
    def get_top_and_worst_assets(user_id: int):
        """
        Compute the top five and worst five assets by profit, excluding assets with an average price of zero.
        Additionally:
            - Exclude assets where Portfolio_Percentage is below 0.5%.
            - Exclude assets named ["EUR", "USDT", "USD", "USDC"].

        Profit is calculated as:
            Profit = (Today_Price - Average_Price) * Amount
        Profit percentage is calculated as:
            Profit_Percentage = ((Today_Price - Average_Price) / Average_Price) * 100

        This method uses PortfolioService.get_user_assets(user_id) to fetch the asset data.
        If get_user_assets returns a list, it is converted to a DataFrame.
        The result is cached in Redis for one hour.
        """
        redis_client = RedisService.get_client()
        cache_key = f"top_worst_assets:user:{user_id}"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Retrieve asset data; get_user_assets might return a list of dictionaries.
        assets_data = PortfolioService.get_user_assets(user_id)
        if isinstance(assets_data, list):
            df_assets = pd.DataFrame(assets_data)
        else:
            df_assets = assets_data

        if df_assets.empty:
            result = {"message": "No assets found for this user."}
            redis_client.setex(cache_key, 3600, json.dumps(result))
            return result

        # Ensure there is a 'Today_Price' column. If not, fetch today's prices from Binance.
        if 'Today_Price' not in df_assets.columns:
            prices = BinanceService.get_all_prices()  # Expected dictionary: { 'BTC': price, ... }
            df_assets['Today_Price'] = df_assets['Asset'].apply(lambda x: prices.get(x, 0))

        # Exclude assets with zero average price.
        df_filtered = df_assets[df_assets['Average_Price'] != 0]
        if df_filtered.empty:
            result = {"message": "No assets with non-zero average price found."}
            redis_client.setex(cache_key, 3600, json.dumps(result))
            return result

        # Calculate profit and profit percentage.
        df_filtered = df_filtered.copy()  # To avoid SettingWithCopyWarning.
        df_filtered['Profit'] = (df_filtered['Today_Price'] - df_filtered['Average_Price']) * df_filtered['Amount']
        df_filtered['Profit_Percentage'] = ((df_filtered['Today_Price'] - df_filtered['Average_Price']) / 
                                            df_filtered['Average_Price']) * 100

        # Exclude assets with Portfolio_Percentage below 0.5%
        if 'Portfolio_Percentage' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Portfolio_Percentage'] >= 0.5]

        # Exclude assets with specific names
        excluded_assets = ["EUR", "USDT", "USD", "USDC"]
        df_filtered = df_filtered[~df_filtered['Asset'].isin(excluded_assets)]

        if df_filtered.empty:
            result = {"message": "No assets found after applying filters."}
            redis_client.setex(cache_key, 3600, json.dumps(result))
            return result

        # Sort to get top 5 (highest profit) and worst 5 (lowest profit).
        df_top = df_filtered.sort_values('Profit', ascending=False).head(5)
        df_worst = df_filtered.sort_values('Profit', ascending=True).head(5)

        result = {
            "top_assets": df_top.to_dict(orient='records'),
            "worst_assets": df_worst.to_dict(orient='records')
        }
        redis_client.setex(cache_key, 3600, json.dumps(result))
        return result

    @staticmethod
    def get_top_assets_significant_price_change(user_id: int, min_price_change: float = 15, top_n: int = 5):
        """
        Returns the top assets (up to top_n) where the price change percentage between yesterday and today
        is greater than min_price_change. Also computes the profit percentage as:
            ((Today_Price - Average_Price) / Average_Price) * 100.
        Only assets with a non-zero Average_Price are considered.
        The result is cached in Redis for one hour.
        """
        redis_client = RedisService.get_client()
        cache_key = f"top_assets_significant:user:{user_id}:min_change:{min_price_change}:top_n:{top_n}"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Retrieve asset data from get_user_assets (which returns a list/dict of asset info)
        assets_data = PortfolioService.get_user_assets(user_id)
        if isinstance(assets_data, list):
            df_assets = pd.DataFrame(assets_data)
        else:
            df_assets = assets_data

        if df_assets.empty:
            result = {"message": "No assets found for this user."}
            redis_client.setex(cache_key, 3600, json.dumps(result))
            return result

        # Instantiate BinanceService to fetch prices.
        binance = BinanceService()

        # Ensure 'Today_Price' exists; if not, fetch today's prices.
        if 'Today_Price' not in df_assets.columns:
            today_prices = binance.get_all_prices()  # Expected dict: { 'BTC': price, ... }
            df_assets['Today_Price'] = df_assets['Asset'].apply(lambda x: today_prices.get(x, 0))

        # Ensure 'Yesterday_Price' exists; if not, fetch yesterday's prices.
        if 'Yesterday_Price' not in df_assets.columns:
            yesterday_prices = binance.get_all_prev_close_prices()  # Expected dict: { 'BTC': price, ... }
            df_assets['Yesterday_Price'] = df_assets['Asset'].apply(lambda x: yesterday_prices.get(x, 0))

        # Exclude assets with zero Average_Price to avoid division by zero.
        df_filtered = df_assets[df_assets['Average_Price'] != 0]
        if df_filtered.empty:
            result = {"message": "No assets with non-zero average price found."}
            redis_client.setex(cache_key, 3600, json.dumps(result))
            return result

        df_filtered = df_filtered.copy()

        # Calculate price change percentage: ((Today_Price - Yesterday_Price) / Yesterday_Price) * 100
        df_filtered['Price_Change_Percentage'] = df_filtered.apply(
            lambda row: ((row['Today_Price'] - row['Yesterday_Price']) / row['Yesterday_Price'] * 100)
                        if row['Yesterday_Price'] != 0 else 0,
            axis=1
        )
        # Calculate profit percentage: ((Today_Price - Average_Price) / Average_Price) * 100
        df_filtered['Profit_Percentage'] = df_filtered.apply(
            lambda row: ((row['Today_Price'] - row['Average_Price']) / row['Average_Price'] * 100)
                        if row['Average_Price'] != 0 else 0,
            axis=1
        )

        # Filter to only include assets where the price change percentage is greater than min_price_change.
        df_significant = df_filtered[df_filtered['Price_Change_Percentage'] > min_price_change]

        # Sort the filtered assets by Profit_Percentage in descending order and take top_n.
        df_top = df_significant.sort_values('Profit_Percentage', ascending=False).head(top_n)

        result = {
            "top_assets": df_top.to_dict(orient='records')
        }
        redis_client.setex(cache_key, 3600, json.dumps(result))
        return result