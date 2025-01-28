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
