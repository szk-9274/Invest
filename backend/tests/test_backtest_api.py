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


class TestStrategyProfilesEndpoint:
    def test_returns_strategy_profiles_from_config(self):
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/backtest/strategies")

        assert response.status_code == 200
        data = response.json()
        strategy_names = [item["strategy_name"] for item in data["strategies"]]
        assert "rule-based-stage2" in strategy_names
        assert "buffett-quality" in strategy_names

        buffett = next(item for item in data["strategies"] if item["strategy_name"] == "buffett-quality")
        assert buffett["display_name"] == "Warren Buffett"
        assert buffett["is_trader_strategy"] is True
        assert buffett["icon_key"] == "brain"

        minervini = next(item for item in data["strategies"] if item["strategy_name"] == "minervini-trend")
        assert minervini["is_current_baseline"] is True
        assert minervini["result_strategy_name"] == "rule-based-stage2"
        assert minervini["portrait_asset_key"] == "minervini"


class TestBacktestRunMetadata:
    def test_get_results_by_timestamp_includes_run_metadata(self, tmp_path):
        import json

        from app import app
        from fastapi.testclient import TestClient

        result_dir = tmp_path / "backtest_2026-01-01_to_2026-01-31_20260131-000000"
        result_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [
                {
                    "ticker": "AAA",
                    "entry_date": "2026-01-01",
                    "entry_price": 10,
                    "exit_date": "2026-01-05",
                    "exit_price": 12,
                    "exit_reason": "rule",
                    "shares": 1,
                    "pnl": 2,
                    "pnl_pct": 20,
                }
            ]
        ).to_csv(result_dir / "trades.csv", index=False)
        pd.DataFrame(
            [
                {"date": "2026-01-01", "action": "ENTRY", "ticker": "AAA", "price": 10, "shares": 1, "pnl": 0},
                {"date": "2026-01-05", "action": "EXIT", "ticker": "AAA", "price": 12, "shares": 1, "pnl": 2},
            ]
        ).to_csv(result_dir / "trade_log.csv", index=False)
        pd.DataFrame(
            [{"ticker": "AAA", "total_pnl": 2, "trade_count": 1, "num_trades": 1, "win_rate": 1.0}]
        ).to_csv(result_dir / "ticker_stats.csv", index=False)
        (result_dir / "run_manifest.json").write_text(
            json.dumps(
                {
                    "run_id": result_dir.name,
                    "run_label": "baseline-run",
                    "experiment_name": "qlib-inspired",
                    "strategy_name": "rule-based-stage2",
                    "benchmark_enabled": True,
                    "rule_profile": "strict-auto-fallback",
                    "tags": ["baseline"],
                    "spec": {
                        "start_date": "2026-01-01",
                        "end_date": "2026-01-31",
                    },
                    "metrics": {
                        "total_trades": 1,
                        "winning_trades": 1,
                        "losing_trades": 0,
                        "win_rate": 1.0,
                        "total_pnl": 2.0,
                        "avg_win": 2.0,
                        "avg_loss": 0.0,
                        "final_capital": 100002.0,
                        "total_return_pct": 0.00002,
                        "annual_return_pct": 0.18,
                        "information_ratio": 1.25,
                        "max_drawdown_pct": -0.08,
                    },
                }
            ),
            encoding="utf-8",
        )

        client = TestClient(app)
        with patch("api.backtest.DEFAULT_OUTPUT_DIR", str(tmp_path)):
            response = client.get("/api/backtest/results/20260131-000000")

        assert response.status_code == 200
        data = response.json()
        assert data["run_metadata"]["run_label"] == "baseline-run"
        assert data["run_metadata"]["experiment_name"] == "qlib-inspired"
        assert data["run_metadata"]["strategy_name"] == "rule-based-stage2"
        assert data["summary"]["annual_return_pct"] == 0.18
        assert data["summary"]["information_ratio"] == 1.25
        assert data["summary"]["max_drawdown_pct"] == -0.08
        assert data["visualization"]["equity_curve"][0]["time"] == "2026-01-01"
        assert data["visualization"]["equity_curve"][-1]["value"] == 100002.0
        assert data["visualization"]["signal_events"][0]["action"] == "ENTRY"
        assert data["visualization"]["signal_events"][-1]["action"] == "EXIT"
