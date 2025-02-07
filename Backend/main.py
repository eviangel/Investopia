from fastapi import FastAPI
from api.routes import portfolio, transactions, binance
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8081"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(binance.router, prefix="/api/binance", tags=["Binance"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

#redis server should be running  on win (redis-server --dir /tmp/) on linux (redis-server)
#or start it without saving (redis-cli config set stop-writes-on-bgsave-error no)