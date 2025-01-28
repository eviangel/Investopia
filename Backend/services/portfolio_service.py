from services.binance_service import BinanceService
from db.db_handler import DatabaseHandler
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
                        price = binance.get_coin_price(asset_name)

                        # Insert or update the asset in the database
                        db.insert_or_update_asset(
                            user_id=user_id,
                            asset_name=asset_name,
                            amount=total_amount,
                            avg_price=price,
                        )
        except Exception as e:
            print(f"Error syncing portfolio for user {user_id}: {e}")
        finally:
            db.close()
