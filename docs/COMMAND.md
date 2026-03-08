# COMMAND.md
Invest プロジェクト コマンド一覧

---

# Backtest Dashboard (Web UI)

## 開発環境での起動
複数のターミナルを開いて以下を実行してください（順番は関係ありません）

### just で一括起動（推奨）
```bash
cd $HOME/code/Invest
just dev
```
- `just dev` は `./devinit.sh` を呼び出し、tmux セッション `invest` を起動/再接続します。
- tmux は 5 ペイン構成で起動します（上段: backend / frontend / copilot、下段: logs / git）。
- `lazygit` が未インストールの場合は `devinit.sh` がエラー終了します。

### just 補助コマンド
```bash
cd $HOME/code/Invest
just stop   # tmux kill-session -t invest
just logs   # tail -F backend.log frontend.log
just test   # cd python && source .venv/bin/activate && pytest
just lint   # cd python && source .venv/bin/activate && ruff check .
just fmt    # cd python && source .venv/bin/activate && ruff format .
```

### ターミナル1：バックエンドAPI起動
```bash
cd $HOME/code/Invest
# Option A (推奨): start uvicorn from repository root so package imports resolve naturally
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Option B: if you prefer starting from the backend directory, set PYTHONPATH to the repo root
# cd $HOME/code/Invest/backend
# PYTHONPATH=$HOME/code/Invest python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
- API サーバーは http://localhost:8000 で起動します（同一ネットワーク端末からはホストIP:8000 でもアクセス可能）
- ホットリロード対応

### ターミナル2：フロントエンド開発サーバー起動
```bash
cd $HOME/code/Invest/python
source .venv/bin/activate
cd $HOME/code/Invest/frontend
npm run dev -- --host 0.0.0.0 --port 3000 --strictPort
```
- React アプリは http://localhost:3000 で起動します（同一ネットワーク端末からはホストIP:3000 でもアクセス可能）
- ホットリロード対応

### devinit.sh の logs ペイン確認
`./devinit.sh` 利用時、logs ペインは以下を同時追尾します。
```bash
tail -F $HOME/code/Invest/backend.log $HOME/code/Invest/frontend.log
```

### devinit.sh の git ペイン確認
`./devinit.sh` 利用時、git ペインは以下を実行します。
```bash
lazygit
```

## ブラウザでアクセス
```
http://localhost:3000/dashboard
http://localhost:3000/home
http://localhost:3000/home?lang=ja
http://localhost:3000/dashboard?lang=ja
```

## API エンドポイントテスト
```bash
# 最新のバックテスト結果を取得
curl http://localhost:8000/api/backtest/latest

# 利用可能なバックテスト一覧を取得
curl http://localhost:8000/api/backtest/list

# 特定のタイムスタンプの結果を取得
curl http://localhost:8000/api/backtest/results/20260303-221229
```

## ダッシュボード機能
- **サイドバー**: バックテスト実行履歴の一覧表示
- **Python Command Runner**: バックテスト / スクリーニング / チャート生成 / 銘柄更新を引数付きで実行
- **ジョブステータス表示**: queued / running / succeeded / failed / cancelled / timeout
- **Live Logs**: 実行ログを画面内でリアルタイム確認
- **Summary タブ**: 統計情報（勝率、損益、シャープレシオなど）
- **Charts タブ**: Plotly ベースの TOP5/BOTTOM5 購入散布図（/dashboard のみ適用、点サイズは購入額連動）
- **Trades タブ**: 全トレード詳細テーブル（ソート・ページネーション対応）

### /dashboard チャート確認（Task1）
```bash
cd $HOME/code/Invest/frontend
# チャート関連ユニットテスト
npm run test -- src/components/TopBottomPurchaseCharts.test.tsx
# フロントエンドビルド確認
npm run build
```

### Python Command Runner の使い方
1. `http://localhost:3000/dashboard` を開く
2. 左サイドバー上部の **Python Command Runner** でコマンドを選択
3. 必要なオプションを入力して **Run Command** をクリック
4. **Status** と **Live Logs** で進捗を確認
5. 停止したい場合は **Cancel Running Job** をクリック

実行できる主なコマンド:
- `backtest` (`--start`, `--end`, `--tickers`, `--no-charts`)
- `stage2` (`--with-fundamentals`)
- `full`
- `chart` (`--ticker`, `--start`, `--end`)
- `update_tickers` (`--min-market-cap`, `--max-tickers`)

## デバッグ・トラブルシューティング

### ブラウザ開発者ツール
```
http://localhost:3000/dashboard で F12 キーを押す
- Console タブで JavaScript エラーを確認
- Network タブで API リクエスト/レスポンスを確認
```

### API ステータス確認
```bash
# バックエンドが起動しているか確認
curl http://localhost:8000/health

# 特定の API エンドポイントが動作しているか確認
curl -i http://localhost:8000/api/backtest/list

# ジョブ一覧取得
curl http://localhost:8000/api/jobs

# ジョブ作成（backtest）
curl -X POST http://localhost:8000/api/jobs -H "Content-Type: application/json" -d "{\"command\":\"backtest\",\"start_date\":\"2024-01-01\",\"end_date\":\"2024-12-31\"}"

# ジョブ状態取得
curl http://localhost:8000/api/jobs/<job_id>

# ジョブログ取得
curl http://localhost:8000/api/jobs/<job_id>/logs

# ジョブキャンセル
curl -X POST http://localhost:8000/api/jobs/<job_id>/cancel
```

### フロントエンドログ確認
ターミナル2（npm run dev）を見て、以下のようなエラーがないか確認：
```
[VITE] error: ...
```

### WSL2 でスマホから :3000 にアクセスできない場合（Windows 側）
管理者 PowerShell で以下を実行：
```powershell
# WSL の eth0 IP を確認（例: 172.31.145.34）
wsl -d Ubuntu -- hostname -I

# 既存の 3000 転送を削除（存在しない場合はエラーで問題なし）
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=3000

# Windows 0.0.0.0:3000 -> WSL_IP:3000 を転送
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3000 connectaddress=<WSL_IP> connectport=3000

# Windows Firewall で 3000/TCP を許可
New-NetFirewallRule -DisplayName "WSL Vite 3000" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
```
- WSL IP は再起動で変わるため、接続できなくなったら `connectaddress` を再設定してください。
- 疎通確認: `http://<WindowsのLAN IP>:3000` または `http://<WindowsのTailscale IP>:3000`

### キャッシュのクリア
```bash
# Python キャッシュ削除
cd python
rm -rf __pycache__
rm -rf .pytest_cache

# Node.js キャッシュ削除
cd frontend
npm cache clean --force
rm -rf node_modules
npm install
```

---

# Electron / Frontend 関連

## 開発起動
```bash
npm run tsc:watch
npm run renderer:dev
npm run electron:dev
```

## 製品版相当の確認
```bash
npm run start:prod
```
## ビルド
```bash
npm run build
```

※ `renderer-dist/` が生成される
## release削除
```bash
rm -rf release
```
## インストーラー生成
```bash
npm run dist
```

---

# Python 環境セットアップ

```bash
cd $HOME/code/Invest/python
# 仮想環境作成（初回のみ）
python -m venv .venv
# 環境構築
pip install -r requirements.txt
# 仮想環境起動
source .venv/bin/activate
```

---

# テスト実行

```bash
# 全テスト実行
pytest
# 特定のテスト
pytest tests/test_ticker_fetcher_smoke.py -v
# カバレッジ付き
pytest --cov=. --cov-report=html
```

---
# Pythonデバックコマンド
# 銘柄リスト更新

```bash
python scripts/update_tickers_extended.py
# オプション指定
python scripts/update_tickers_extended.py --min-market-cap 5000000000
python scripts/update_tickers_extended.py --min-market-cap 5000000000 --max-tickers 2000
```

# Stage2 スクリーニング
```bash
python main.py --mode stage2
python main.py --mode stage2 --with-fundamentals

# # クイックテスト
# python main.py --mode test
# # Stage2 + VCP
# python main.py --mode full
```

#　Backtest　+ 自動チャート生成
```bash
# デフォルト期間
python main.py --mode backtest
# 期間指定
python main.py --mode backtest --start 2023-01-01 --end 2024-01-01
python main.py --mode backtest --start 2022-01-01 --end 2024-12-31
# 特定銘柄のみ
python main.py --mode backtest --tickers AAPL,MSFT,NVDA
## チャート生成スキップ
python main.py --mode backtest --no-charts
## 特定銘柄チャート生成
python main.py --mode chart --ticker AAPL
## 期間指定チャート
python main.py --mode chart --ticker AAPL --start 2023-01-01 --end 2024-01-01
# フォールバック動作テスト
ログ内の `[FALLBACK]` を確認
```

# BACKTEST UI verification

- Start frontend dev server:
  npm --prefix frontend run dev

- Run frontend tests (only TopBottom tests):
  npm --prefix frontend run test -- --testNamePattern TopBottomPurchaseCharts

- Capture screenshots (desktop/mobile):
  node scripts/capture-screenshot.js --url http://localhost:5173/dashboard --out tests/screenshots --sizes "1280x720,375x812"

Notes:
- All API calls must be mocked during unit tests.
