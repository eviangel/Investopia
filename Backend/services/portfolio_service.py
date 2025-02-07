from services.binance_service import BinanceService
from db.db_handler import DatabaseHandler
import pandas as pd
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)

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
                    if asset_name in ["USDT", "NFT"]:
                        continue
                    logging.info(f"Asset: {asset_name}, Total: {total_amount}")

                    if total_amount > 0:
                        # Fetch the current price of the asset
                        # price = binance.get_coin_price(asset_name)
                        avg_price = binance.check_average_price(asset_name)
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

    @staticmethod
    def get_user_assets(user_id):
        """
        Fetches user assets from the database.

        Parameters:
        - user_id: The ID of the user.

        Returns:
        - A list of user assets containing:
            - Asset (Symbol)
            - Average_Price (User’s recorded price)
            - Amount (Total held)
            - Today_Price (Current price from Binance)
            - Total_Value (Value of this asset in USD)
            - Portfolio_Percentage (Percentage of total portfolio)
        """
        db = DatabaseHandler()
        binance = BinanceService()

        try:
            df_assets = db.get_user_assets(user_id)

            if df_assets.empty:
                return {"message": "No assets found for this user."}

            # Fetch all Binance prices at once
            prices = binance.get_all_prices()

            # Assign prices to each asset, ensuring missing prices get `0`
            df_assets['Today_Price'] = df_assets['Asset'].apply(lambda x: prices.get(x, 0))

            # Ensure Average_Price is not NULL
            df_assets['Average_Price'].fillna(0, inplace=True)

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