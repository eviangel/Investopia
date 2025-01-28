from db.db_handler import DatabaseHandler

def setup_test_user(db, user_id):
    """
    Ensure a test user exists in the database.
    """
    db.cursor.execute(
        "INSERT IGNORE INTO Users (UserID, API, Secret, Username) VALUES (%s, %s, %s, %s)",
        (user_id, 'dummy_api_key', 'dummy_secret', 'test_user')
    )
    db.db_connection.commit()

def cleanup_test_data(db, user_id):
    """
    Delete test data for the given user ID.
    """
    db.cursor.execute("DELETE FROM Asset WHERE UserID = %s", (user_id,))
    db.cursor.execute("DELETE FROM Transaction WHERE UserID = %s", (user_id,))
    db.db_connection.commit()

def test_insert_asset_data():
    db = DatabaseHandler()
    user_id = 999
    setup_test_user(db, user_id)
    
    try:
        db.insert_asset_data("BTC", 1, user_id, 35000)
        db.cursor.execute("SELECT * FROM Asset WHERE UserID = %s AND Name = 'BTC'", (user_id,))
        result = db.cursor.fetchone()
        print(result)
        assert result is not None
        assert result[1] == "BTC"
        assert result[2] == 1
        assert result[3] == user_id
        assert result[4] == 35000.0
    finally:
        cleanup_test_data(db, user_id)
        db.close()

def test_transaction_exists():
    db = DatabaseHandler()
    user_id = 999
    setup_test_user(db, user_id)

    try:
        
        db.insert_asset_data("BTC", 2, user_id, 35000)
        # Insert dummy transaction
        db.cursor.execute(
            """
            INSERT INTO Transaction (AssetID, UserID, Time, Quantity, Price, Action, Commission)
            VALUES ((SELECT id FROM Asset WHERE Name = 'BTC' AND UserID = %s), %s, '2025-01-01 12:00:00', '2', '35000', 'BUY', '10')
            """,
            (user_id,user_id)
        )
        db.db_connection.commit()

        exists = db.transaction_exists("BTC", user_id, "2025-01-01 12:00:00", "2")
        assert exists is True

        not_exists = db.transaction_exists("ETH", user_id, "2025-01-01 12:00:00", "2")
        assert not_exists is False
    finally:
        cleanup_test_data(db, user_id)
        db.close()

def test_asset_exists_and_update():
    db = DatabaseHandler()
    user_id = 999
    setup_test_user(db, user_id)

    try:
        # Insert initial asset data
        db.insert_asset_data("BTC", 1.0, user_id, 35000)
        
        # Update asset data
        updated = db.asset_exists_and_update("BTC", 2.0)
        assert updated is True

        db.cursor.execute("SELECT Amount FROM Asset WHERE Name = 'BTC' AND UserID = %s", (user_id,))
        result = db.cursor.fetchone()
        print(result)
        assert result[0] == 2.0
    finally:
        cleanup_test_data(db, user_id)
        db.close()

def test_insert_transaction_if_not_exists():
    db = DatabaseHandler()
    user_id = 999
    setup_test_user(db, user_id)

    try:
        # Insert an asset for the test user
        db.insert_asset_data("BTC", 1.0, user_id, 35000)

        # Insert a transaction
        db.insert_transaction_if_not_exists("test_user", "BTC", "2025-01-01 12:00:00", "0.5", "35000", "BUY", "10")

        # Verify the transaction exists
        db.cursor.execute(
            """
            SELECT * FROM Transaction WHERE UserID = %s AND AssetID = (
                SELECT id FROM Asset WHERE Name = 'BTC' AND UserID = %s
            )
            """,
            (user_id,user_id)
        )
        result = db.cursor.fetchone()
        print("Transaction fetched:", result)
        assert result is not None
        assert result[2] == user_id  # UserID
    finally:
        cleanup_test_data(db, user_id)
        db.close()

# Ensure the tests only run when executed directly
if __name__ == "__main__":
    test_insert_asset_data()
    test_transaction_exists()
    test_insert_transaction_if_not_exists()
    test_asset_exists_and_update()
