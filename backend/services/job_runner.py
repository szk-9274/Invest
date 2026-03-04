import os
import shlex
import subprocess
import sys
import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from loguru import logger


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PYTHON_DIR = os.path.join(BASE_DIR, "python")
JOB_LOG_DIR = os.path.join(PYTHON_DIR, "output", "job_runs")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobRunner:
    def __init__(self) -> None:
        self._jobs: Dict[str, Dict] = {}
        self._processes: Dict[str, subprocess.Popen] = {}
        self._lock = threading.Lock()
        os.makedirs(JOB_LOG_DIR, exist_ok=True)

    def _build_command(self, payload: Dict) -> List[str]:
        command = payload.get("command")
        argv: List[str] = []

        if command == "backtest":
            argv = ["main.py", "--mode", "backtest"]
            if payload.get("start_date"):
                argv.extend(["--start", payload["start_date"]])
            if payload.get("end_date"):
                argv.extend(["--end", payload["end_date"]])
            if payload.get("tickers"):
                argv.extend(["--tickers", payload["tickers"]])
            if payload.get("no_charts"):
                argv.append("--no-charts")
            return argv

        if command == "stage2":
            argv = ["main.py", "--mode", "stage2"]
            if payload.get("with_fundamentals"):
                argv.append("--with-fundamentals")
            return argv

        if command == "full":
            argv = ["main.py", "--mode", "full"]
            return argv

        if command == "chart":
            ticker = payload.get("ticker")
            if not ticker:
                raise ValueError("ticker is required for chart command")
            argv = ["main.py", "--mode", "chart", "--ticker", ticker]
            if payload.get("start_date"):
                argv.extend(["--start", payload["start_date"]])
            if payload.get("end_date"):
                argv.extend(["--end", payload["end_date"]])
            return argv

        if command == "update_tickers":
            argv = ["scripts/update_tickers_extended.py"]
            if payload.get("min_market_cap") is not None:
                argv.extend(["--min-market-cap", str(payload["min_market_cap"])])
            if payload.get("max_tickers") is not None:
                argv.extend(["--max-tickers", str(payload["max_tickers"])])
            return argv

        raise ValueError(f"Unsupported command: {command}")

    def _shell_preview(self, argv: List[str]) -> str:
        safe_argv = [sys.executable] + argv
        return " ".join(shlex.quote(a) for a in safe_argv)

    def create_job(self, payload: Dict) -> Dict:
        argv = self._build_command(payload)
        job_id = str(uuid.uuid4())
        created_at = _utc_now()
        timeout_seconds = int(payload.get("timeout_seconds") or 7200)
        log_path = os.path.join(JOB_LOG_DIR, f"{job_id}.log")

        job = {
            "job_id": job_id,
            "command": payload.get("command"),
            "args": payload,
            "command_line": self._shell_preview(argv),
            "status": "queued",
            "created_at": created_at,
            "started_at": None,
            "finished_at": None,
            "return_code": None,
            "error": None,
            "timeout_seconds": timeout_seconds,
            "log_path": log_path,
            "cancel_requested": False,
        }

        with self._lock:
            self._jobs[job_id] = job

        thread = threading.Thread(
            target=self._run_job,
            args=(job_id, argv, timeout_seconds, log_path),
            daemon=True,
        )
        thread.start()

        return self.get_job(job_id)

    def _run_job(self, job_id: str, argv: List[str], timeout_seconds: int, log_path: str) -> None:
        full_cmd = [sys.executable] + argv
        start_ts = datetime.now(timezone.utc)

        with self._lock:
            job = self._jobs[job_id]
            job["status"] = "running"
            job["started_at"] = _utc_now()

        logger.info(f"Starting job {job_id}: {' '.join(full_cmd)}")
        try:
            with open(log_path, "w", encoding="utf-8") as log_file:
                process = subprocess.Popen(
                    full_cmd,
                    cwd=PYTHON_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                with self._lock:
                    self._processes[job_id] = process

                while True:
                    line = process.stdout.readline() if process.stdout else ""
                    if line:
                        log_file.write(line)
                        log_file.flush()

                    elapsed = (datetime.now(timezone.utc) - start_ts).total_seconds()
                    with self._lock:
                        current = self._jobs[job_id]
                        cancel_requested = current.get("cancel_requested", False)

                    if cancel_requested and process.poll() is None:
                        process.terminate()
                        with self._lock:
                            current = self._jobs[job_id]
                            current["status"] = "cancelled"
                            current["error"] = "Cancelled by user"

                    if elapsed > timeout_seconds and process.poll() is None:
                        process.terminate()
                        with self._lock:
                            current = self._jobs[job_id]
                            current["status"] = "timeout"
                            current["error"] = f"Timeout after {timeout_seconds}s"

                    if line == "" and process.poll() is not None:
                        break

                return_code = process.wait()
                with self._lock:
                    current = self._jobs[job_id]
                    if current["status"] == "running":
                        current["status"] = "succeeded" if return_code == 0 else "failed"
                        if return_code != 0:
                            current["error"] = f"Process exited with code {return_code}"
                    current["return_code"] = return_code
                    current["finished_at"] = _utc_now()
                logger.info(f"Job {job_id} finished with code {return_code}")
        except Exception as exc:
            logger.exception(f"Job {job_id} crashed: {exc}")
            with self._lock:
                current = self._jobs[job_id]
                current["status"] = "failed"
                current["error"] = str(exc)
                current["finished_at"] = _utc_now()
        finally:
            with self._lock:
                self._processes.pop(job_id, None)

    def cancel_job(self, job_id: str) -> Dict:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(job_id)

            job = self._jobs[job_id]
            if job["status"] in {"succeeded", "failed", "cancelled", "timeout"}:
                return dict(job)

            job["cancel_requested"] = True

        return self.get_job(job_id)

    def list_jobs(self, limit: int = 50) -> List[Dict]:
        with self._lock:
            jobs = [dict(job) for job in self._jobs.values()]
        jobs.sort(key=lambda item: item["created_at"], reverse=True)
        return jobs[:limit]

    def get_job(self, job_id: str) -> Dict:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(job_id)
            return dict(self._jobs[job_id])

    def get_job_logs(self, job_id: str, tail: int = 200) -> Dict:
        job = self.get_job(job_id)
        log_path = job.get("log_path")
        if not log_path or not os.path.exists(log_path):
            return {
                "job_id": job_id,
                "status": job["status"],
                "lines": [],
            }

        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        return {
            "job_id": job_id,
            "status": job["status"],
            "lines": [line.rstrip("\n") for line in lines[-tail:]],
        }


job_runner = JobRunner()
