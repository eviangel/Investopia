import mysql.connector
import logging

class DatabaseHandler:
    logging.basicConfig(level=logging.INFO)
    def __init__(self):
        self.db_connection = mysql.connector.connect(
            user="root",
            password="11",
            host="localhost",
            database="database",
        )
        self.cursor = self.db_connection.cursor(buffered=True)

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
        - asset_name: Name of the asset (e.g., BTC, ETH).
        - time: Timestamp of the transaction.
        - quantity: Quantity of the asset in the transaction.
        - price: Price of the asset in the transaction.
        - action: Transaction type (e.g., BUY, SELL).
        - commission: Commission paid for the transaction.
        """
        # Get the UserID from the username
        user_id = self.get_user_id_by_username(username)
        if not user_id:
            print("Transaction insertion failed: User not found.")
            return

        # Get the AssetID from the asset name
        query_get_asset_id = "SELECT id FROM Asset WHERE Name = %s AND UserID = %s"
        self.cursor.execute(query_get_asset_id, (asset_name, user_id))
        asset_id_result = self.cursor.fetchone()

        if not asset_id_result:
            print(f"Transaction insertion failed: Asset '{asset_name}' not found for user.")
            return

        asset_id = asset_id_result[0]

        # Check if the transaction already exists
        query_check_transaction = """
        SELECT COUNT(*) FROM Transaction
        WHERE AssetID = %s AND UserID = %s AND Time = %s AND Quantity = %s
        """
        self.cursor.execute(query_check_transaction, (asset_id, user_id, time, quantity))
        exists = self.cursor.fetchone()[0]

        if not exists:
            # Insert the transaction if it doesn't exist
            query_insert_transaction = """
            INSERT INTO Transaction (AssetID, UserID, Time, Quantity, Price, Action, Commission)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query_insert_transaction, (asset_id, user_id, time, quantity, price, action, commission))
            self.db_connection.commit()
            print(f"Transaction for asset '{asset_name}' inserted successfully.")
        else:
            print(f"Transaction for asset '{asset_name}' already exists.")

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
