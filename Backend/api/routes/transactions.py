from fastapi import APIRouter, HTTPException
from services.transaction_service import TransactionService

router = APIRouter()

@router.post("/sync")
def sync_transactions(user_id: int, api_key: str, api_secret: str):
    """
    Sync all transactions for a user from Binance using symbols fetched from the database.
    """
    try:
        TransactionService.sync_transactions(user_id, api_key, api_secret)
        return {"message": "Transactions synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing transactions: {e}")



#to modified later on:
@router.get("/getuser_deposits_withdraw_{user_id}")
def get_user_depo_withdrow_transactions(user_id: int):
    """
    API to fetch all deposits and withdrawals for a user.

    Parameters:
    - user_id (int): The ID of the user.

    Returns:
    - JSON with withdrawals & deposits.
    """
    try:
        transactions = TransactionService.get_user_transaction_history(user_id)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#to modified later on:
@router.get("/getuser_crypto_deposits_withdraw_{user_id}")
def get_user_crypto_depo_transactions(user_id: int):
    """
    API to fetch all deposits and withdrawals for a user.

    Parameters:
    - user_id (int): The ID of the user.

    Returns:
    - JSON with withdrawals & deposits.
    """
    try:
        transactions = TransactionService.get_user_transaction_history(user_id)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))