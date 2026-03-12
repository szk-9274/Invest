# COMMAND.md

MinerviLism プロジェクトの主要コマンド集です。すべてリポジトリルート `~/code/MinerviLism` を基準にしています。

## 1. 開発環境をまとめて起動

```bash
cd ~/code/MinerviLism
just dev
```

停止とログ確認:

```bash
just stop
just logs
```

tmux を直接操作する場合:

```bash
tmux ls
tmux detach
tmux kill-session -t minervilism
tmux kill-server
```

## 2. backend API を起動

```bash
cd ~/code/MinerviLism
./python/.venv/bin/python3 -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

疎通確認:

```bash
curl http://localhost:8000/health
```

成果物ディレクトリを差し替える場合:

```bash
cd ~/code/MinerviLism
MINERVILISM_OUTPUT_DIR=/absolute/path/to/backtest ./python/.venv/bin/python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

## 3. frontend を起動

```bash
cd ~/code/MinerviLism/frontend
npm run dev -- --host 0.0.0.0 --port 3000 --strictPort
```

## 4. Python CLI を実行

```bash
cd ~/code/MinerviLism/python
./.venv/bin/python3 main.py --mode backtest
./.venv/bin/python3 main.py --mode backtest --start 2023-01-01 --end 2023-12-31
./.venv/bin/python3 main.py --mode backtest --start 2023-01-01 --end 2023-12-31 --run-label baseline-2023
./.venv/bin/python3 main.py --mode backtest --no-charts
./.venv/bin/python3 main.py --mode chart --ticker AAPL --start 2023-01-01 --end 2023-12-31
./.venv/bin/python3 scripts/update_tickers_extended.py --min-market-cap 5000000000
```

バックテスト実行後は `python/output/backtest/<run>/run_manifest.json` と `python/output/backtest/registry.json` を見ると、実行条件・主要指標・成果物一覧を確認できます。

## 5. OpenAPI 契約から frontend 型を再生成

```bash
cd ~/code/MinerviLism
./python/.venv/bin/python3 -m backend.scripts.export_frontend_contracts
```

## 6. Electron を使う

```bash
cd ~/code/MinerviLism
npm install
npm run build
npm run dev
npm run start:prod
```

## 7. Docker Compose で起動

```bash
cd ~/code/MinerviLism
docker compose up --build
```

個別起動:

```bash
docker compose up backend frontend
```

## 8. テストと検証

backend:

```bash
cd ~/code/MinerviLism
./python/.venv/bin/python3 -m pytest backend/tests -q
./python/.venv/bin/python3 -m pytest backend/tests --cov=backend --cov-report=term --cov-fail-under=80
./python/.venv/bin/python3 -m pytest tests -q
```

frontend:

```bash
cd ~/code/MinerviLism
npm --prefix frontend run build
npm --prefix frontend run test -- --run
npm --prefix frontend run test:coverage
```

documentation:

```bash
cd ~/code/MinerviLism
./python/.venv/bin/python3 scripts/doc_gardening.py
./python/.venv/bin/python3 scripts/check_docs.py
```

contract drift:

```bash
cd ~/code/MinerviLism
./python/.venv/bin/python3 -m backend.scripts.export_frontend_contracts
git diff -- frontend/src/api/generated/contracts.ts
```

full stack / Electron:

```bash
cd ~/code/MinerviLism
npm run test:e2e
npm run build
```

screenshot capture:

```bash
cd ~/code/MinerviLism
./python/.venv/bin/python3 -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5174 --strictPort
npm run screenshot:ci
```

Docker / CI 相当確認:

```bash
cd ~/code/MinerviLism
docker compose config
docker compose build
```

## 9. よく使う just コマンド

```bash
cd ~/code/MinerviLism
just dev
just stop
just logs
just test
just lint
just fmt
```
