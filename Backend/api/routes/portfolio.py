from fastapi import APIRouter, HTTPException
from services.portfolio_service import PortfolioService

router = APIRouter()

@router.post("/portfolio/sync")
def sync_portfolio(user_id: int, api_key: str, api_secret: str):
    try:
        PortfolioService.sync_portfolio(user_id, api_key, api_secret)
        return {"message": "Portfolio synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing portfolio: {e}")
