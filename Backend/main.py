from fastapi import FastAPI
from api.routes import portfolio, transactions, binance

app = FastAPI()

app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(binance.router, prefix="/api/binance", tags=["Binance"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
