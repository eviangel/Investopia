from fastapi import FastAPI
from api.routes import portfolio, transactions, binance,user
from fastapi.middleware.cors import CORSMiddleware



from fastapi_utils.tasks import repeat_every
from services.portfolio_service import PortfolioService
from db.db_handler import DatabaseHandler
app = FastAPI()
@app.on_event("startup")
@repeat_every(seconds=86400)  # Run once every 24 hours
def update_daily_performance():
    """
    Scheduled task to update daily performance for all users once per day.
    """
    db = DatabaseHandler()
    try:
        query = "SELECT DISTINCT UserID FROM Asset"
        db.cursor.execute(query)
        users = db.cursor.fetchall()
        for user in users:
            PortfolioService.get_daily_performance(user[0])  # Update cache for each user
        print("✅ Daily performance updated for all users.")
    except Exception as e:
        print(f"❌ Error updating daily performance: {e}")
    finally:
        db.close()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)




app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(binance.router, prefix="/api/binance", tags=["Binance"])
app.include_router(user.router, prefix="/api/user", tags=["User"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

#redis server should be running  on win (redis-server --dir /tmp/) on linux (redis-server)
#or start it without saving (redis-cli config set stop-writes-on-bgsave-error no)