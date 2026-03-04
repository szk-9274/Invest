from unittest.mock import patch


class TestJobsApi:
    def test_create_job(self):
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        mocked_job = {
            "job_id": "job-123",
            "command": "backtest",
            "command_line": "python main.py --mode backtest",
            "status": "queued",
            "created_at": "2026-03-04T00:00:00+00:00",
            "started_at": None,
            "finished_at": None,
            "return_code": None,
            "error": None,
            "timeout_seconds": 7200,
            "args": {},
            "log_path": "dummy",
            "cancel_requested": False,
        }

        with patch("api.jobs.job_runner.create_job", return_value=mocked_job):
            response = client.post(
                "/api/jobs",
                json={
                    "command": "backtest",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                },
            )

        assert response.status_code == 200
        payload = response.json()
        assert payload["job_id"] == "job-123"
        assert payload["status"] == "queued"

    def test_get_job(self):
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        mocked_job = {
            "job_id": "job-234",
            "command": "stage2",
            "command_line": "python main.py --mode stage2",
            "status": "running",
            "created_at": "2026-03-04T00:00:00+00:00",
            "started_at": "2026-03-04T00:00:01+00:00",
            "finished_at": None,
            "return_code": None,
            "error": None,
            "timeout_seconds": 7200,
            "args": {},
            "log_path": "dummy",
            "cancel_requested": False,
        }

        with patch("api.jobs.job_runner.get_job", return_value=mocked_job):
            response = client.get("/api/jobs/job-234")

        assert response.status_code == 200
        payload = response.json()
        assert payload["job_id"] == "job-234"
        assert payload["status"] == "running"

    def test_get_job_logs(self):
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        with patch(
            "api.jobs.job_runner.get_job_logs",
            return_value={"job_id": "job-1", "status": "running", "lines": ["a", "b"]},
        ):
            response = client.get("/api/jobs/job-1/logs?tail=50")

        assert response.status_code == 200
        payload = response.json()
        assert payload["lines"] == ["a", "b"]

    def test_cancel_job(self):
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        mocked_job = {
            "job_id": "job-999",
            "command": "full",
            "command_line": "python main.py --mode full",
            "status": "cancelled",
            "created_at": "2026-03-04T00:00:00+00:00",
            "started_at": "2026-03-04T00:00:01+00:00",
            "finished_at": "2026-03-04T00:00:02+00:00",
            "return_code": None,
            "error": "Cancelled by user",
            "timeout_seconds": 7200,
            "args": {},
            "log_path": "dummy",
            "cancel_requested": True,
        }

        with patch("api.jobs.job_runner.cancel_job", return_value=mocked_job):
            response = client.post("/api/jobs/job-999/cancel")

        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"


class TestBacktestRunCompatibility:
    def test_backtest_run_returns_job_id(self):
        from app import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        with patch(
            "api.backtest.run_backtest_task",
            return_value={
                "status": "started",
                "message": "Backtest queued",
                "job_id": "job-777",
            },
        ):
            response = client.post(
                "/api/backtest/run",
                json={"start_date": "2024-01-01", "end_date": "2024-12-31"},
            )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "started"
        assert payload["job_id"] == "job-777"
