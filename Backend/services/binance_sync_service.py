from services.binance_service import BinanceService
from db.db_handler import DatabaseHandler
from datetime import datetime

class BinanceSyncService:
    @staticmethod
    def sync_all(user_id, api_key, api_secret):
        db = DatabaseHandler()
        binance = BinanceService(api_key, api_secret)

        try:
            # Fetch symbols dynamically
            symbols = db.fetch_symbols(user_id, binance)

            # Sync portfolio and transactions
            for symbol in symbols:
                trades = binance.get_trade_history(symbol)
                for trade in trades:
                    asset_name = symbol.replace("USDT", "")
                    time = datetime.utcfromtimestamp(trade["time"] / 1000).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    qty = float(trade["qty"])
                    price = float(trade["price"])
                    is_buyer = "BUY" if trade["isBuyer"] else "SELL"
                    commission = trade["commission"]

                    db.insert_transaction_if_not_exists(
                        user_id=user_id,
                        asset_name=asset_name,
                        time=time,
                        quantity=qty,
                        price=price,
                        action=is_buyer,
                        commission=commission,
                    )

            print(f"Portfolio and transactions synced for user {user_id}.")
        except Exception as e:
            print(f"Error syncing data for user {user_id}: {e}")
        finally:
            db.close()

