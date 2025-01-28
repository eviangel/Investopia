from db.db_handler import DatabaseHandler
from services.binance_service import BinanceService
from datetime import datetime

class TransactionService:
    @staticmethod
    def sync_transactions(user_id, api_key, api_secret):
        """
        Sync all transactions for a user from Binance using symbols fetched from the database.

        Parameters:
        - user_id: ID of the user in the database.
        - api_key: Binance API key.
        - api_secret: Binance API secret.
        """
        db = DatabaseHandler()
        binance = BinanceService(api_key, api_secret)

        try:
            # Fetch symbols from the database
            symbols = db.fetch_symbols_from_db(user_id)

            for symbol in symbols:
                asset_name = symbol.replace("USDT", "")  # Extract the asset name
                trades = binance.get_trade_history(symbol)  # Fetch trade history

                for trade in trades:
                    # Prepare transaction data
                    time = datetime.utcfromtimestamp(trade["time"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    qty = float(trade["qty"])
                    price = float(trade["price"])
                    is_buyer = "BUY" if trade["isBuyer"] else "SELL"
                    commission = trade["commission"]
                    db_username = db.get_username_by_user_id(user_id)
                    # Insert transaction into the database
                    db.insert_transaction_if_not_exists(
                        username=db_username,
                        asset_name=asset_name,
                        time=time,
                        quantity=qty,
                        price=price,
                        action=is_buyer,
                        commission=commission
                    )
            print("Transactions synced successfully.")
        except Exception as e:
            print(f"Error syncing transactions: {e}")
        finally:
            db.close()
