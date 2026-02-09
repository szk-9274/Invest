"""
Tests for Phase B-1: Backtest API Endpoints

Tests cover:
1. POST /api/backtest/run - Backtest execution endpoint
2. GET /api/backtest/results - Result retrieval
3. GET /api/backtest/tickers - Top/Bottom tickers endpoint
4. Input validation
"""
import pytest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Backend must be first on path to avoid collision with python/main.py
_backend_dir = str(Path(__file__).parent.parent)
_python_dir = str(Path(__file__).parent.parent.parent / "python")
if _backend_dir in sys.path:
    sys.path.remove(_backend_dir)
sys.path.insert(0, _backend_dir)
if _python_dir not in sys.path:
    sys.path.append(_python_dir)

import pandas as pd


class TestBacktestRunEndpoint:
    """Tests for POST /api/backtest/run."""

    def test_endpoint_exists(self):
        """POST /api/backtest/run should be registered."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        # Should not return 404 (405 Method Not Allowed is acceptable for wrong method)
        response = client.post(
            "/api/backtest/run",
            json={"start_date": "2024-01-01", "end_date": "2024-12-31"},
        )
        assert response.status_code != 404

    def test_requires_dates(self):
        """POST /api/backtest/run should require start_date and end_date."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.post("/api/backtest/run", json={})
        assert response.status_code == 422  # Validation error

    def test_accepts_valid_dates(self):
        """POST /api/backtest/run should accept valid date inputs."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        with patch("api.backtest.run_backtest_task") as mock_run:
            mock_run.return_value = {
                "status": "started",
                "message": "Backtest started",
            }
            response = client.post(
                "/api/backtest/run",
                json={"start_date": "2024-01-01", "end_date": "2024-12-31"},
            )
            # Should return 200 or 202 (Accepted)
            assert response.status_code in (200, 202)


class TestBacktestResultsEndpoint:
    """Tests for GET /api/backtest/results."""

    def test_endpoint_exists(self):
        """GET /api/backtest/results should be registered."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        with patch("api.backtest.load_results") as mock_load:
            mock_load.return_value = {
                "trade_log": [],
                "ticker_stats": [],
                "has_results": False,
            }
            response = client.get("/api/backtest/results")
            assert response.status_code != 404

    def test_returns_results_when_available(self):
        """GET /api/backtest/results should return trade data when available."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        with patch("api.backtest.load_results") as mock_load:
            mock_load.return_value = {
                "trade_log": [],
                "ticker_stats": [],
                "has_results": True,
            }
            response = client.get("/api/backtest/results")
            assert response.status_code == 200
            data = response.json()
            assert "has_results" in data

    def test_returns_empty_when_no_results(self):
        """GET /api/backtest/results should indicate no results when none exist."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        with patch("api.backtest.load_results") as mock_load:
            mock_load.return_value = {
                "trade_log": [],
                "ticker_stats": [],
                "has_results": False,
            }
            response = client.get("/api/backtest/results")
            assert response.status_code == 200
            data = response.json()
            assert data["has_results"] is False


class TestTickersEndpoint:
    """Tests for GET /api/backtest/tickers."""

    def test_endpoint_exists(self):
        """GET /api/backtest/tickers should be registered."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/backtest/tickers")
        assert response.status_code != 404

    def test_returns_top_bottom_tickers(self):
        """GET /api/backtest/tickers should return top and bottom tickers."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        with patch("api.backtest.load_top_bottom_tickers") as mock_load:
            mock_load.return_value = {
                "top": [
                    {"ticker": "AAPL", "total_pnl": 5000.0},
                    {"ticker": "MSFT", "total_pnl": 3000.0},
                ],
                "bottom": [
                    {"ticker": "BAD1", "total_pnl": -2000.0},
                    {"ticker": "BAD2", "total_pnl": -3000.0},
                ],
            }
            response = client.get("/api/backtest/tickers")
            assert response.status_code == 200
            data = response.json()
            assert "top" in data
            assert "bottom" in data
            assert len(data["top"]) == 2
            assert len(data["bottom"]) == 2
