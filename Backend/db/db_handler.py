import mysql.connector
import logging
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import bcrypt
import datetime
from jose import jwt
from config.config import Config

class DatabaseHandler:
    logging.basicConfig(level=logging.INFO)
    def __init__(self):
        self.db_connection = mysql.connector.connect(
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            port = 3306,
            use_pure=True
        )
        self.cursor = self.db_connection.cursor(buffered=True)
        # Create an SQLAlchemy engine for Pandas queries
        try:
            # self.engine = create_engine("mysql+pymysql://root:11@127.0.0.1/database")
            self.engine = create_engine(Config.DATABASE_URL)
        except Exception as e:
            print(f"Error creating SQLAlchemy engine: {e}")

    def get_user_id_by_username(self, username):
        query = "SELECT UserID FROM Users WHERE Username = %s"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_username_by_user_id(self, user_id):
        """
        Fetch the username for a given user ID.

        Parameters:
        - user_id: The ID of the user.

        Returns:
        - The username if it exists, otherwise None.
        """
        query = "SELECT Username FROM Users WHERE UserID = %s"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def asset_exists_and_update(self, asset_name, new_amount):
        query_check = "SELECT Amount FROM Asset WHERE Name = %s"
        self.cursor.execute(query_check, (asset_name,))
        result = self.cursor.fetchone()

        if result: 
            if result[0] != new_amount:
                query_update = "UPDATE Asset SET Amount = %s WHERE Name = %s"
                self.cursor.execute(query_update, (new_amount, asset_name))
                self.db_connection.commit()
                return True
            return False
        else:
            return False

    def insert_or_update_asset(self, user_id, asset_name, amount, avg_price):
        """
        Insert a new asset or update an existing asset for a user in the Asset table.

        Parameters:
        - user_id: The ID of the user.
        - asset_name: The name of the asset (e.g., BTC).
        - amount: The total amount of the asset.
        - avg_price: The average price of the asset.
        """
        # Check if the asset already exists for the user
        query_check = "SELECT COUNT(*) FROM Asset WHERE Name = %s AND UserID = %s"
        self.cursor.execute(query_check, (asset_name, user_id))
        exists = self.cursor.fetchone()[0]

        if exists:
            # Update the existing asset
            query_update = """
            UPDATE Asset
            SET Amount = %s, Average_Price = %s
            WHERE Name = %s AND UserID = %s
            """
            self.cursor.execute(query_update, (amount, avg_price, asset_name, user_id))
        else:
            # Insert a new asset
            query_insert = """
            INSERT INTO Asset (Name, Amount, UserID, Average_Price)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query_insert, (asset_name, amount, user_id, avg_price))

        # Commit the changes
        self.db_connection.commit()

    def update_portfolio(self, user_id, asset_data):
        """
        Update or insert portfolio data for a user in the Asset table.

        Parameters:
        - user_id: The ID of the user whose portfolio is being updated.
        - asset_data: List of dictionaries with:
            - 'asset_name': Name of the asset.
            - 'amount': Total amount of the asset.
            - 'average_price': Average purchase price of the asset.
        """
        for asset in asset_data:
            asset_name = asset['asset_name']
            amount = asset['amount']
            avg_price = asset['average_price']

            # Check if the asset exists for the user
            query_check = """
            SELECT COUNT(*) FROM Asset WHERE Name = %s AND UserID = %s
            """
            self.cursor.execute(query_check, (asset_name, user_id))
            exists = self.cursor.fetchone()[0]

            if exists:
                # Update existing asset
                query_update = """
                UPDATE Asset
                SET Amount = %s, Average_Price = %s
                WHERE Name = %s AND UserID = %s
                """
                self.cursor.execute(query_update, (amount, avg_price, asset_name, user_id))
            else:
                # Insert new asset
                query_insert = """
                INSERT INTO Asset (Name, Amount, UserID, Average_Price)
                VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(query_insert, (asset_name, amount, user_id, avg_price))

        # Commit changes
        self.db_connection.commit()

    def insert_transaction_if_not_exists(self, username, asset_name, time, quantity, price, action, commission):
        """
        Insert a transaction into the Transaction table if it does not already exist.

        Parameters:
        - username: Username of the user performing the transaction.
        - asset_name: Name of the asset (e.g., BTC, EUR).
        - time: Timestamp of the transaction.
        - quantity: Quantity of the asset in the transaction.
        - price: Price of the asset in the transaction.
        - action: Transaction type (e.g., BUY, SELL, Deposit, Withdrawal).
        - commission: Commission paid for the transaction.
        """
        # Get the UserID from the username
        user_id = self.get_user_id_by_username(username)
        if not user_id:
            print("Transaction insertion failed: User not found.")
            return

        # Ensure the asset exists for this user
        query_get_asset_id = "SELECT id FROM Asset WHERE Name = %s AND UserID = %s"
        self.cursor.execute(query_get_asset_id, (asset_name, user_id))
        asset_id_result = self.cursor.fetchone()

        if not asset_id_result:
            print(f"⚠️ Asset '{asset_name}' not found for user {username}. Inserting it now...")

            # Insert asset with default values if missing
            query_insert_asset = """
            INSERT INTO Asset (Name, Amount, UserID, Average_Price)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query_insert_asset, (asset_name, 0, user_id, 1.0))  # Default amount = 0, avg price = 1.0
            self.db_connection.commit()

            # Fetch the new AssetID
            self.cursor.execute(query_get_asset_id, (asset_name, user_id))
            asset_id_result = self.cursor.fetchone()

        asset_id = asset_id_result[0]

        # Check if the transaction already exists
        query_check_transaction = """
        SELECT COUNT(*) FROM Transaction
        WHERE AssetID = %s AND UserID = %s AND Time = %s AND Quantity = %s
        """
        self.cursor.execute(query_check_transaction, (asset_id, user_id, time, quantity))
        exists = self.cursor.fetchone()[0]

        if not exists:
            # Insert the transaction
            query_insert_transaction = """
            INSERT INTO Transaction (AssetID, UserID, Time, Quantity, Price, Action, Commission)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query_insert_transaction, (asset_id, user_id, time, quantity, price, action, commission))
            self.db_connection.commit()
            print(f"✅ Transaction for asset '{asset_name}' inserted successfully.")
        else:
            print(f"⚠️ Transaction for asset '{asset_name}' already exists.")


    def fetch_symbols(user_id, binance):
        """
        Fetch all unique symbols from Binance and the local database.

        Parameters:
        - user_id: The ID of the user.
        - binance: Instance of BinanceService.

        Returns:
        - A list of unique symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
        """
        db = DatabaseHandler()
        symbols = set()

        try:
            # Fetch symbols from Binance
            logging.info("Fetching symbols from Binance...")
            snapshot = binance.get_account_snapshot("SPOT")
            for snapshot_entry in snapshot.get("snapshotVos", []):
                for balance in snapshot_entry["data"]["balances"]:
                    asset_name = balance["asset"]
                    if float(balance["free"]) > 0 or float(balance["locked"]) > 0:
                        symbols.add(f"{asset_name}USDT")

            logging.info(f"Symbols fetched from Binance: {symbols}")

            # Fetch symbols from the database
            logging.info("Fetching symbols from the database...")
            query = "SELECT Name FROM Asset WHERE UserID = %s"
            db.cursor.execute(query, (user_id,))
            assets = db.cursor.fetchall()
            for row in assets:
                symbols.add(f"{row[0]}USDT")

            logging.info(f"Symbols fetched from the database: {[f'{row[0]}USDT' for row in assets]}")

            # Final symbol list
            logging.info(f"Final list of symbols: {list(symbols)}")
            return list(symbols)
        finally:
            db.close()

    def fetch_symbols_from_db(self,user_id):
        """
        Fetch all unique symbols from the Asset table for a specific user.

        Parameters:
        - user_id: The ID of the user.

        Returns:
        - A list of symbols (e.g., ["BTCUSDT", "ETHUSDT"]).
        """
        db = DatabaseHandler()
        try:
            # Query to fetch asset names for the user
            query = "SELECT Name FROM Asset WHERE UserID = %s"
            db.cursor.execute(query, (user_id,))
            assets = db.cursor.fetchall()

            # Convert asset names to symbols (e.g., "BTC" -> "BTCUSDT")
            symbols = [f"{row[0]}USDT" for row in assets]
            print(f"Symbols fetched from the database for user {user_id}: {symbols}")
            return symbols
        finally:
            db.close()

    def transaction_exists(self, asset_name, user_id, time, quantity):
        """
        Check if a transaction exists for a specific asset, user, time, and quantity.

        Parameters:
        - asset_name: The name of the asset (e.g., BTC).
        - user_id: The ID of the user.
        - time: The timestamp of the transaction.
        - quantity: The quantity of the asset involved in the transaction.

        Returns:
        - True if the transaction exists, False otherwise.
        """
        # Get the AssetID from the asset name
        query_get_asset_id = "SELECT id FROM Asset WHERE Name = %s AND UserID = %s"
        self.cursor.execute(query_get_asset_id, (asset_name, user_id))
        asset_id_result = self.cursor.fetchone()

        if not asset_id_result:
            print(f"Transaction check failed: Asset '{asset_name}' not found for user {user_id}.")
            return False

        asset_id = asset_id_result[0]

        # Check if the transaction exists
        query_check_transaction = """
        SELECT COUNT(*) FROM Transaction
        WHERE AssetID = %s AND UserID = %s AND Time = %s AND Quantity = %s
        """
        self.cursor.execute(query_check_transaction, (asset_id, user_id, time, quantity))
        count = self.cursor.fetchone()[0]
        return count > 0

    def close(self):
        self.cursor.close()
        self.db_connection.close()

    def get_user_assets(self, user_id):
        """
        Retrieve asset details for a user from the database using SQLAlchemy.

        Parameters:
        - user_id: The ID of the user.

        Returns:
        - A Pandas DataFrame containing asset names, average prices, and amounts.
        """
        try:
            query = f"SELECT Name AS Asset, Average_Price, Amount FROM Asset WHERE UserID = {user_id}"
            df = pd.read_sql(query, self.engine)
            print(f"Fetched user assets: {df}")  # Debugging print
            return df
        except Exception as e:
            print(f"Error fetching user assets: {e}")  # Log error
            return pd.DataFrame()  # Return empty DataFrame to prevent crashes

    def get_assets_with_zero_average_price(self, user_id):
        """
        Fetch all assets for a specific user where Average_Price = 0.

        Parameters:
        - user_id: The ID of the user.

        Returns:
        - A list of tuples containing asset details.
        """
        try:
            query = """
                SELECT Name, Amount 
                FROM Asset 
                WHERE UserID = %s AND Average_Price = 0
            """
            self.cursor.execute(query, (user_id,))
            assets = self.cursor.fetchall()
            return [{"Asset": row[0], "Amount": row[1]} for row in assets]
        except Exception as e:
            print(f"Error fetching assets with zero average price: {e}")
            return []

    def insert_or_update_coin(self, symbol, coin_id):
        """
        Insert or update a coin ID in the `coin_mapping` table.
        """
        query = """
            INSERT INTO coin_mapping (symbol, coin_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE coin_id = VALUES(coin_id)
        """
        self.cursor.execute(query, (symbol.upper(), coin_id))
        self.db_connection.commit()

    def get_coin_id(self, symbol):
        """
        Fetch the CoinGecko ID for a given asset symbol from the database.
        """
        query = "SELECT coin_id FROM coin_mapping WHERE symbol = %s"
        self.cursor.execute(query, (symbol.upper(),))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def start_transaction(self):
        """Start a database transaction."""
        self.db_connection.start_transaction()

    def commit_transaction(self):
        """Commit the current database transaction."""
        self.db_connection.commit()

    def rollback_transaction(self):
        """Rollback the current database transaction."""
        self.db_connection.rollback()

    def get_asset_id(self, asset_symbol):
        """
        Get AssetID for a given asset symbol.
        
        Parameters:
        - asset_symbol: The symbol of the asset (e.g., 'BTC', 'ETH').

        Returns:
        - AssetID (int) if found, None otherwise.
        """
        query = "SELECT id FROM Asset WHERE Name = %s LIMIT 1;"
        self.cursor.execute(query, (asset_symbol,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def insert_transactions_bulk(self, transactions):
        """
        Insert multiple transactions in a single query.

        Parameters:
        - transactions: List of tuples containing transaction data.
        """
        query = """
        INSERT IGNORE INTO `Transaction` (AssetID, UserID, Time, Quantity, Price, Action, Commission)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        self.cursor.executemany(query, transactions)
        self.db_connection.commit()  # ✅ Commit after executing batch insert

    def get_all_user_transactions(self, user_id, transaction_type):
        """
        Fetch all transactions (withdraw or deposit) for a user across all exchanges.

        Parameters:
        - user_id (int): The ID of the user.
        - transaction_type: Either 'WITHDRAW' or 'DEPOSIT'.

        Returns:
        - A list of dictionaries containing transaction details.
        """
        query = """
            SELECT t.id, a.Name AS asset, t.Time, t.Quantity, t.Action, t.Commission
            FROM Transaction t
            JOIN Asset a ON t.AssetID = a.id
            WHERE t.UserID = %s AND t.Action = %s
            ORDER BY t.Time DESC
        """
        self.cursor.execute(query, (user_id, transaction_type))
        transactions = self.cursor.fetchall()

        return [
            {
                "transaction_id": row[0],
                "asset": row[1],
                "time": row[2],
                "quantity": row[3],
                "action": row[4],
                "commission": row[5],
            }
            for row in transactions
        ]

   ### 🔹 AUTH METHODS ###
    def create_users_table(self):
        """Ensure the Users table exists"""
        query = """
        CREATE TABLE IF NOT EXISTS Users (
            UserID INT(9) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(100) NOT NULL UNIQUE,
            Email VARCHAR(100) NOT NULL UNIQUE,
            Password_hash VARCHAR(255) NOT NULL,
            Created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(query)
        self.db_connection.commit()

    def register_user(self, username, email, password):
        """Register a new user with hashed password"""
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        query = "INSERT INTO Users (Username, Email, Password_hash) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(query, (username, email, hashed_password))
            self.db_connection.commit()
            return {"message": "User registered successfully"}
        except mysql.connector.Error as e:
            self.db_connection.rollback()  # ✅ Rollback on failure
            return {"error": str(e)}

    def authenticate_user(self, email, password):
        """Authenticate user and return JWT token"""
        query = "SELECT UserID, Username, Password_hash FROM Users WHERE Email = %s"
        self.cursor.execute(query, (email,))
        user = self.cursor.fetchone()

        if user and bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8")):
            token = jwt.encode(
                {"user_id": user[0], "username": user[1], "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
                Config.SECRET_KEY,
                algorithm=Config.ALGORITHM
            )
            return {"access_token": token, "token_type": "bearer"}
        return None

    #end of auth methods
    def update_asset_balance(self, user_id, asset_name, amount, action):
        """
        Update the asset balance in the database based on deposits or withdrawals.

        Parameters:
        - user_id: The ID of the user.
        - asset_name: The name of the asset (e.g., EUR).
        - amount: The deposit/withdrawal amount.
        - action: 'Deposit' or 'Withdrawal'.
        """
        # Fetch the current asset amount
        query_check = "SELECT Amount FROM Asset WHERE Name = %s AND UserID = %s"
        self.cursor.execute(query_check, (asset_name, user_id))
        result = self.cursor.fetchone()

        if result:
            current_amount = float(result[0])
            
            # Update amount based on action
            if action == "Deposit":
                new_amount = current_amount + amount
            elif action == "Withdrawal":
                new_amount = max(0, current_amount - amount)  # Ensure balance doesn't go negative
            
            # Update the asset balance in the database
            query_update = "UPDATE Asset SET Amount = %s WHERE Name = %s AND UserID = %s"
            self.cursor.execute(query_update, (new_amount, asset_name, user_id))
        
        else:
            # If asset does not exist, insert it (only for deposits)
            if action == "Deposit":
                query_insert = "INSERT INTO Asset (Name, Amount, UserID, Average_Price) VALUES (%s, %s, %s, %s)"
                self.cursor.execute(query_insert, (asset_name, amount, user_id, 1.0))  # Default avg_price = 1.0

        self.db_connection.commit()
