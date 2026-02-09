"""
Tests for Phase B-1: Charts API Endpoints

Tests cover:
1. GET /api/charts/{ticker} - Chart data endpoint
2. GET /api/charts/{ticker}/ohlcv - OHLCV data for Plotly rendering
"""
import pytest
import sys
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
import numpy as np


class TestChartDataEndpoint:
    """Tests for GET /api/charts/{ticker}."""

    def test_endpoint_exists(self):
        """GET /api/charts/{ticker} should be registered."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/charts/AAPL")
        assert response.status_code != 404

    def test_returns_chart_data(self):
        """GET /api/charts/{ticker} should return OHLCV data."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        mock_data = {
            "ticker": "AAPL",
            "dates": ["2024-01-02", "2024-01-03"],
            "open": [150.0, 151.0],
            "high": [155.0, 156.0],
            "low": [149.0, 150.0],
            "close": [153.0, 154.0],
            "volume": [1000000, 1100000],
            "sma20": [None, None],
            "sma50": [None, None],
            "sma200": [None, None],
        }

        with patch("api.charts.get_chart_data") as mock_get:
            mock_get.return_value = mock_data
            response = client.get("/api/charts/AAPL")
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "AAPL"
            assert "dates" in data
            assert "open" in data
            assert "close" in data

    def test_accepts_date_range_params(self):
        """GET /api/charts/{ticker} should accept start_date and end_date params."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        with patch("api.charts.get_chart_data") as mock_get:
            mock_get.return_value = {
                "ticker": "AAPL",
                "dates": [],
                "open": [],
                "high": [],
                "low": [],
                "close": [],
                "volume": [],
            }
            response = client.get(
                "/api/charts/AAPL",
                params={"start_date": "2024-01-01", "end_date": "2024-12-31"},
            )
            assert response.status_code == 200


class TestChartTradesEndpoint:
    """Tests for GET /api/charts/{ticker}/trades."""

    def test_endpoint_exists(self):
        """GET /api/charts/{ticker}/trades should be registered."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/charts/AAPL/trades")
        assert response.status_code != 404

    def test_returns_trade_markers(self):
        """GET /api/charts/{ticker}/trades should return entry/exit data."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        with patch("api.charts.get_trade_markers") as mock_get:
            mock_get.return_value = {
                "entries": [
                    {"date": "2024-01-15", "price": 150.0},
                ],
                "exits": [
                    {"date": "2024-02-01", "price": 160.0, "pnl": 1000.0},
                ],
            }
            response = client.get("/api/charts/AAPL/trades")
            assert response.status_code == 200
            data = response.json()
            assert "entries" in data
            assert "exits" in data
