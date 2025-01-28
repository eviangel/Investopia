from fastapi import FastAPI
from api.routes import portfolio, user, binance, transactions

app = FastAPI()

# Include routes
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(binance.router, prefix="/api/binance", tags=["Binance"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
