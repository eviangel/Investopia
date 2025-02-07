from fastapi import APIRouter, HTTPException,Query
from services.portfolio_service import PortfolioService

router = APIRouter()

@router.post("/portfolio/sync")
def sync_portfolio(user_id: int, api_key: str, api_secret: str):
    try:
        PortfolioService.sync_portfolio(user_id, api_key, api_secret)
        return {"message": "Portfolio synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing portfolio: {e}")

@router.get("/daily_performance")
def get_portfolio_daily_performance(
    user_id: int = Query(..., description="User ID for fetching portfolio data")
):
    """
    API endpoint to fetch portfolio daily performance including daily gain/loss percentage.
    """
    try:
        data = PortfolioService.fetch_portfolio_daily_performance(user_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio daily performance: {e}")

@router.get("/user-assets")
def get_user_assets(
    user_id: int = Query(..., description="User ID for fetching user assets")
):
    """
    API endpoint to fetch a user's assets.

    Returns:
    - A JSON response containing:
        - Asset (Symbol)
        - Average_Price (User’s recorded price)
        - Amount (Total held)
        - Today_Price (Current price)
        - Total_Value (Value of this asset in USD)
        - Portfolio_Percentage (Percentage of total portfolio)
    """
    try:
        data = PortfolioService.get_user_assets(user_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user assets: {e}")