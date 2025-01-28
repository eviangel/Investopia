from fastapi import APIRouter,HTTPException
from services.binance_service import BinanceService
from services.binance_sync_service import BinanceSyncService
from services.portfolio_service import PortfolioService
from services.transaction_service import TransactionService

router = APIRouter()

@router.get("/binance/price")
def get_price(symbol: str):
    """Get the current price of a coin."""
    return BinanceService.get_coin_price(symbol)

@router.post("/binance/sync")
def sync_portfolio(user_id: int):
    """Sync portfolio with Binance."""
    return BinanceService.sync_portfolio(user_id)


#Old sync all
# @router.post("/sync-all")
# def sync_all_data(user_id: int, api_key: str, api_secret: str):
#     """
#     Sync all data from Binance, including portfolio and transactions.
#     """
#     try:
#         BinanceSyncService.sync_all(user_id, api_key, api_secret)
#         return {"message": "Portfolio and transactions synced successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error syncing data: {e}")

@router.post("/sync-all")
def sync_all(user_id: int, api_key: str, api_secret: str):
    """
    Sync both portfolio and transactions for a user.
    """
    try:
        # Sync portfolio
        PortfolioService.sync_portfolio(user_id, api_key, api_secret)

        # Sync transactions
        TransactionService.sync_transactions(user_id, api_key, api_secret)

        return {"message": "Portfolio and transactions synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing data: {e}")