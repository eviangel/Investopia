from fastapi import APIRouter, HTTPException,Query
from services.portfolio_service import PortfolioService
from services.coingecko_service import CoinGeckoService

router = APIRouter()

@router.post("/portfolio/sync")
def sync_portfolio(user_id: int, api_key: str, api_secret: str):
    try:
        PortfolioService.sync_portfolio(user_id, api_key, api_secret)
        return {"message": "Portfolio synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing portfolio: {e}")

@router.get("/old_daily_performance")
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

@router.post("/set-average-price")
def set_average_price(
    user_id: int = Query(..., description="User ID"),
    asset_name: str = Query(..., description="Asset symbol (e.g., BTC)"),
    avg_price: float = Query(..., description="New average price")
):
    """
    API endpoint to update the average price for a specific asset for a user.
    If the asset exists, only the average price is updated unless amount is explicitly provided.

    Example request:
    ```
    # Update only the average price
    POST /api/portfolio/set-average-price?user_id=1&asset_name=BTC&avg_price=32000
    ```
    """
    try:
        data = PortfolioService.set_average_price(user_id, asset_name, avg_price)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating average price: {e}")

@router.get("/zero-average-price-assets")
def get_assets_with_zero_avg_price(
    user_id: int = Query(..., description="User ID")
):
    """
    API endpoint to fetch all assets for a user where Average_Price = 0.

    Example request:
    ```
    GET /api/portfolio/zero-average-price-assets?user_id=1
    ```
    """
    try:
        data = PortfolioService.get_assets_with_zero_avg_price(user_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assets: {e}")

@router.get("/daily-performance")
def get_daily_performance(user_id: int = Query(..., description="User ID for fetching daily performance")):
    """
    API endpoint to fetch daily performance of a user's portfolio.

    Example request:
    ```
    GET /api/portfolio/daily-performance?user_id=1
    ```
    """
    try:
        data = PortfolioService.get_daily_performance(user_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily performance: {e}")

@router.get("/coin-chart")
def get_coin_chart(
    asset: str = Query(..., description="Asset symbol (e.g., BTC, ETH)"),
    days: int = Query(7, description="Number of days for historical data (1 to 30)")
):
    """
    API endpoint to fetch historical price data for an asset.

    Example request:
    ```
    GET /api/portfolio/coin-chart?asset=bitcoin&days=7
    ```

    Response:
    ```
    [
        [timestamp, price],
        [timestamp, price],
        ...
    ]
    ```
    """
    try:
        data = PortfolioService.get_historical_prices(asset, days)

        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error"])

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")

@router.post("/update-coin-list")
def update_coin_list():
    """
    API endpoint to fetch the top 1000 coins from CoinGecko and update them in MySQL.

    Example request:
    ```
    POST /api/portfolio/update-coin-list
    ```

    Response:
    ```
    {"message": "Coin list updated successfully."}
    ```
    """
    try:
        CoinGeckoService.update_coin_list()
        return {"message": "Coin list updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating coin list: {str(e)}")

@router.get("/period-balance")
def get_period_balance(
    user_id: int = Query(..., description="User ID for fetching balance"),
    days: int = Query(365, description="Number of days for balance calculation (e.g., 30, 365, etc.)")
):
    """
    API endpoint to fetch the user's portfolio balance for each day in the past `days` days.
    Returns a list of dictionaries with:
      - date (YYYY-MM-DD)
      - total_balance (USD value)
    """
    try:
        data = PortfolioService.get_period_balance_with_history(user_id, days)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching balance: {e}")

@router.get("/top-worst-assets")
def get_top_worst_assets(
    user_id: int = Query(..., description="User ID for fetching top and worst assets")
):
    """
    API endpoint to fetch the top five and worst five assets by profit.
    Profit is calculated as: (Today_Price - Average_Price) * Amount.
    Assets with an average price of zero are excluded.
    The result is cached for one hour.
    """
    try:
        data = PortfolioService.get_top_and_worst_assets(user_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top/worst assets: {e}")

@router.get("/top-assets-significant")
def get_top_assets_significant(
    user_id: int = Query(..., description="User ID for fetching top assets with significant price change"),
    min_price_change: float = Query(15, description="Minimum price change percentage between yesterday and today (default: 15)"),
    top_n: int = Query(5, description="Number of top assets to return (default: 5)")
):
    """
    API endpoint to fetch the top assets where the price change percentage between yesterday and today
    is greater than a specified threshold (default 15%). For each asset, also return the profit percentage,
    calculated as ((Today_Price - Average_Price) / Average_Price) * 100.
    The result is cached for one hour.
    """
    try:
        data = PortfolioService.get_top_assets_significant_price_change(user_id, min_price_change, top_n)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top significant assets: {e}")