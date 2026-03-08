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
import sys
from pathlib import Path

# Ensure backend directory and repository root are on sys.path so 'api' and 'python' packages can be imported
FILE_PATH = Path(__file__).resolve()
BACKEND_DIR = FILE_PATH.parent
REPO_ROOT = FILE_PATH.parents[1]
# Only adjust sys.path when module is executed as a script (not when imported as a package via -m).
# When running as a package (e.g., `python -m uvicorn backend.app:app`), __package__ is set and
# the import system will resolve package imports correctly.
if not __package__:
    for _p in (str(BACKEND_DIR), str(REPO_ROOT)):
        if _p not in sys.path:
            sys.path.insert(0, _p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.backtest import router as backtest_router
from api.charts import router as charts_router
from api.jobs import router as jobs_router

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
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(backtest_router)
app.include_router(charts_router)
app.include_router(jobs_router)


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
