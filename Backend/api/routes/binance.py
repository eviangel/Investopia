from fastapi import APIRouter,HTTPException,Query
from services.binance_service import BinanceService
from services.binance_sync_service import BinanceSyncService
from services.portfolio_service import PortfolioService
from services.transaction_service import TransactionService
from datetime import datetime, timedelta
from db.db_handler import DatabaseHandler

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

@router.get("/fiat_deposits-withdrawals")
def fetch_fiat_withdraws_deposits(user_id: int,
    api_key: str,
    api_secret: str,
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format (default: 2 years ago)"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format (default: Today)")):
    """
    Fetch all Binance Fiat withdrawals & deposits for a user and store them in the database.

    Parameters:
    - user_id (int): The ID of the user.
    - api_key (str): Binance API Key.
    - api_secret (str): Binance API Secret.
    - start_date (str, optional): Start date in `YYYY-MM-DD` format. Default: 2 years ago.
    - end_date (str, optional): End date in `YYYY-MM-DD` format. Default: Today.
    """
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")  # 2 years ago
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")  # Today
    binanceservice = BinanceService(api_key, api_secret)
    return BinanceService.get_fiat_transactions(binanceservice,user_id, start_date, end_date)


@router.get("/crypto_deposits-withdrawals")
def fetch_crypto_withdraws_deposits(user_id: int,
    api_key: str,
    api_secret: str,
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format (default: 2 years ago)"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format (default: Today)")):
    """
    Fetch all Binance crypto withdrawals & deposits for a user and store them in the database.

    Parameters:
    - user_id (int): The ID of the user.
    - api_key (str): Binance API Key.
    - api_secret (str): Binance API Secret.
    - start_date (str, optional): Start date in `YYYY-MM-DD` format. Default: 2 years ago.
    - end_date (str, optional): End date in `YYYY-MM-DD` format. Default: Today.
    """
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")  # 2 years ago
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")  # Today
    binance_service = BinanceService(api_key, api_secret)
    return BinanceService.fetch_crypto_transactions_for_period(binance_service,user_id, start_date, end_date)