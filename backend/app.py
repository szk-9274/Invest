"""
FastAPI Main Application Entry Point

Phase B-1: Minimal Web Application Foundation

Provides:
- Health check endpoint
- API info endpoint
- CORS middleware for React frontend
- Backtest API router
- Charts API router
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.backtest import router as backtest_router
from api.charts import router as charts_router

app = FastAPI(
    title="Invest Backtest API",
    version="0.1.0",
    description="API for stock screening and backtesting system",
)

# CORS middleware for React frontend (localhost dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(backtest_router)
app.include_router(charts_router)


@app.get("/")
def root():
    """API root - returns basic info."""
    return {
        "name": "Invest Backtest API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
