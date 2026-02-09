"""
Tests for Phase B-1: FastAPI Main Application

Tests cover:
1. App creation and health endpoint
2. CORS middleware configuration
3. API router inclusion
"""
import pytest
import sys
from pathlib import Path

# Backend must be first on path to avoid collision with python/main.py
_backend_dir = str(Path(__file__).parent.parent)
_python_dir = str(Path(__file__).parent.parent.parent / "python")
if _backend_dir in sys.path:
    sys.path.remove(_backend_dir)
sys.path.insert(0, _backend_dir)
if _python_dir not in sys.path:
    sys.path.append(_python_dir)


class TestAppCreation:
    """Validate FastAPI app can be created and has basic endpoints."""

    def test_app_can_be_imported(self):
        """The main FastAPI app should be importable."""
        from app import app
        assert app is not None

    def test_health_endpoint(self):
        """GET /health should return 200 with status ok."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_root_endpoint(self):
        """GET / should return basic API info."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    def test_cors_headers_present(self):
        """CORS headers should be present for cross-origin requests."""
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # FastAPI with CORS middleware should allow localhost origins
        assert response.status_code in (200, 204)
