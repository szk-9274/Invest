# Invest

Invest は、Python の分析・バックテスト基盤、FastAPI の API 層、React の可視化 UI、Electron のデスクトップ実行導線をまとめた株式分析ワークスペースです。Python が生成した成果物を backend が API 化し、frontend と Electron が同じ契約に基づいて表示します。

## 概要

このリポジトリでは次のことができます。

- Python CLI でバックテストや関連処理を実行する
- 実行条件・指標・成果物一覧を `run_manifest.json` / `registry.json` として保存する
- `python/output/` 配下の成果物を backend から参照する
- FastAPI の OpenAPI 契約から frontend 向け TypeScript 型を生成する
- React ダッシュボードでサマリ、チャート、トレード一覧、ジョブ状態を確認する
- Electron 用ビルドを作成し、renderer を同梱したデスクトップ実行フローを使う
- Docker Compose で backend と frontend をまとめて起動する

## アーキテクチャ

責務はレイヤごとに分離されています。

- `python/`: 分析ロジック、バックテスト、実験メタデータ、成果物生成
- `backend/`: `python/output/` の成果物を読む FastAPI アプリ
- `frontend/`: React + TypeScript による可視化 UI
- `electron/`: Electron メインプロセス
- `docs/`: 設計、品質、運用ドキュメント

基本的なデータフローは次のとおりです。

1. Python が `python/output/backtest/...` に成果物と `run_manifest.json` を出力し、`registry.json` を更新する
2. backend が `ResultStore` を通じて成果物と run metadata を解決する
3. FastAPI が OpenAPI 契約付きでレスポンスを返す
4. frontend が生成済み TypeScript 契約を使って結果を描画する
5. Electron は build 済み renderer を読み込んで同じ UI を表示する

## ディレクトリ構成

```text
.
├── backend/                # FastAPI アプリ、API、services、schema、tests
├── electron/               # Electron メインプロセス
├── frontend/               # React アプリ、API クライアント、pages、component tests
├── python/                 # 分析ロジック、CLI、設定、experiments、出力、requirements
├── scripts/                # 補助スクリプト
├── tests/                  # 共有 fixture など
├── Dockerfile.backend      # backend 用コンテナ定義
├── Dockerfile.frontend     # frontend 用コンテナ定義
├── docker-compose.yml      # frontend + backend のローカル起動導線
├── justfile                # 開発コマンドのショートカット
└── package.json            # Electron / ルートワークフロー用スクリプト
```

## 前提環境

推奨環境は以下です。

- Python 3.10 以上
- Node.js 20 以上
- npm
- just
- tmux
- lazygit
- Docker / Docker Compose（Compose 起動を使う場合のみ）

## セットアップ

### 1. リポジトリを取得

```bash
git clone <your-ssh-repo-url>
cd Invest
```

### 2. Python 仮想環境を作成

```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

### 3. frontend 依存を導入

```bash
npm --prefix frontend install
```

### 4. Electron / ルート依存を導入

```bash
npm install
```

## 開発起動

### tmux ベースでまとめて起動

```bash
just dev
```

`devinit.sh` が tmux セッションを作成し、backend / frontend / copilot / logs / git の各ペインを起動します。

### 停止とログ確認

```bash
just stop
just logs
```

## Python CLI

Python 実行前に仮想環境を有効化してください。

```bash
cd python
source .venv/bin/activate
```

主な実行例:

```bash
python main.py --mode backtest
python main.py --mode backtest --start 2023-01-01 --end 2023-12-31
python main.py --mode backtest --start 2023-01-01 --end 2023-12-31 --run-label baseline-2023
python main.py --mode backtest --no-charts
python main.py --mode chart --ticker AAPL --start 2023-01-01 --end 2023-12-31
python scripts/update_tickers_extended.py --min-market-cap 5000000000
```

成果物は主に `python/output/` 配下へ保存されます。Qlib の recorder 思想を軽量化した形として、各バックテスト run は条件スナップショットと成果物一覧を `run_manifest.json` に保存し、`python/output/backtest/registry.json` に run サマリを集約します。

```text
python/output/backtest/
├── registry.json
└── backtest_YYYY-MM-DD_to_YYYY-MM-DD_YYYYMMDD-HHMMSS/
    ├── run_manifest.json
    ├── trades.csv
    ├── trade_log.csv
    ├── ticker_stats.csv
    └── charts/
```

## backend API

リポジトリルートから起動します。

```bash
cd python
source .venv/bin/activate
cd ..
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

主なエンドポイント:

- `GET /health`
- `GET /api/backtest/latest`
- `GET /api/backtest/results/{timestamp}`
- `GET /api/backtest/list`
- `GET /api/backtest/tickers`
- `GET /api/charts/{ticker}`
- `GET /api/charts/{ticker}/trades`
- `POST /api/jobs`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/logs`
- `POST /api/jobs/{job_id}/cancel`

出力ディレクトリを切り替えたい場合は `INVEST_OUTPUT_DIR` を指定します。

```bash
INVEST_OUTPUT_DIR=/absolute/path/to/backtest python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

## OpenAPI 契約と frontend 型生成

backend の OpenAPI schema から frontend 用 TypeScript 契約を再生成できます。

```bash
cd python
source .venv/bin/activate
cd ..
python -m backend.scripts.export_frontend_contracts
```

生成先:

- `frontend/src/api/generated/contracts.ts`

backend の response schema を変更したら、この生成を再実行して frontend 側と同期してください。

## frontend

開発サーバー起動:

```bash
npm --prefix frontend run dev -- --host 0.0.0.0 --port 3000 --strictPort
```

主な画面:

- `/` - バックテスト実行と上位/下位銘柄のホーム画面
- `/home` - ホーム画面の別ルート
- `/dashboard` - KPI 概要、条件比較、実験一覧テーブル、ジョブ状態を表示するダッシュボード
- `/dashboard/analysis` - エクイティカーブ、ドローダウン、シグナルイベント、チャートギャラリー、トレード一覧を表示する詳細画面
- `/chart/:ticker` - 個別銘柄チャート

localhost 可視化で使うデータ I/O 契約:

- 実験メタデータ: `GET /api/backtest/list`
  - `timestamp`, `period`, `run_label`, `experiment_name`, `strategy_name`, `rule_profile`, `headline_metrics`
- 結果概要と詳細: `GET /api/backtest/latest`, `GET /api/backtest/results/{timestamp}`
  - `summary`: 総トレード数、勝率、年率、IR、MDD、最終資産など
  - `visualization`: `equity_curve`, `drawdown`, `signal_events`
- 画像成果物: `charts` フィールドから PNG を参照

保存先とパス規約:

```text
python/output/backtest/{run_id}/
├── run_manifest.json      # 実験ID、期間、条件名、評価指標、成果物一覧
├── trades.csv             # 約定サマリ
├── trade_log.csv          # ENTRY / EXIT イベント時系列
├── ticker_stats.csv       # 銘柄別集計
└── charts/*.png           # 補助画像チャート
```

初回イテレーションでは backend が `run_manifest.json` / CSV を読み、frontend が直接描画しやすい JSON（`headline_metrics`, `visualization`）へ整形して返します。ローカルで fixture や別の成果物を読みたい場合は `INVEST_OUTPUT_DIR` で参照先を切り替えてください。

ビルドとテスト:

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
npm --prefix frontend run test:coverage
```

## Electron

Electron メインプロセスは `electron/main.ts` で管理され、renderer は `frontend/dist` から `renderer-dist/` へコピーされます。

主なコマンド:

```bash
npm run build
npm run dev
npm run start:prod
```

- `npm run build`: Electron main と frontend renderer をまとめてビルド
- `npm run dev`: TypeScript watch + Vite dev server + Electron を同時起動
- `npm run start:prod`: build 後に Electron を本番相当で起動

## Docker Compose

Docker が利用可能な環境では、backend と frontend を次で起動できます。

```bash
docker compose up --build
```

個別起動例:

```bash
docker compose up backend frontend
```

Compose 構成では frontend が `VITE_DEV_PROXY_TARGET=http://backend:8000` を使い、backend は `/app/python/output/backtest` を `INVEST_OUTPUT_DIR` として参照します。

## テストと検証

主要な検証コマンド:

```bash
cd python && source .venv/bin/activate && cd .. && pytest backend/tests -q
cd python && source .venv/bin/activate && cd .. && pytest tests -q
npm --prefix frontend run build
npm --prefix frontend run test -- --run
npm --prefix frontend run test:coverage
npm run test:e2e
npm run build
```

`npm run test:e2e` は fixture を backend に読み込ませ、frontend ダッシュボードが実データを描画できることを確認します。

## Documentation system

このリポジトリは大きな単一マニュアルではなく、索引と責務分離を前提にした知識ベースとしてドキュメントを管理します。

- [docs/DOCUMENTATION_SYSTEM.md](docs/DOCUMENTATION_SYSTEM.md) - ドキュメント構造の入口
- [ARCHITECTURE.md](ARCHITECTURE.md) - どの層に何を書くかの地図
- [docs/design-docs/index.md](docs/design-docs/index.md) - 設計判断の索引
- [docs/exec-plans/active/index.md](docs/exec-plans/active/index.md) - 進行中の実装計画
- [docs/exec-plans/completed/index.md](docs/exec-plans/completed/index.md) - 完了済みの実装計画
- [docs/product-specs/index.md](docs/product-specs/index.md) - 仕様書の索引
- [docs/generated/doc-inventory.md](docs/generated/doc-inventory.md) - 自動生成されるドキュメント在庫表

ドキュメント整合性は `python scripts/check_docs.py` で検証し、機械的に更新できる索引・在庫表は `python scripts/doc_gardening.py` で再生成します。

## CI / GitHub Actions

`.github/workflows/ci.yml` では次を自動検証します。

- backend test + coverage fail-under 80
- OpenAPI からの contract 再生成差分チェック
- frontend build / test:coverage
- fixture ベース E2E
- root `npm run build`
- `docker compose config` と `docker compose build`
- `python scripts/check_docs.py` によるドキュメント整合性チェック

`.github/workflows/docs-governance.yml` では、push / pull_request で docs lint を実行し、schedule / workflow_dispatch では doc-gardening を走らせて差分を自動 PR 化します。

契約差分をローカルで確認したい場合:

```bash
cd python
source .venv/bin/activate
cd ..
python -m backend.scripts.export_frontend_contracts
git diff -- frontend/src/api/generated/contracts.ts
```

ドキュメント在庫表と索引の再生成:

```bash
cd python
source .venv/bin/activate
cd ..
python scripts/doc_gardening.py
python scripts/check_docs.py
```

## 参考ドキュメント

- [ARCHITECTURE.md](ARCHITECTURE.md) - システム構造と責務分離
- [docs/DOCUMENTATION_SYSTEM.md](docs/DOCUMENTATION_SYSTEM.md) - ドキュメント構造と鮮度維持ルール
- [COMMAND.md](COMMAND.md) - 手動実行コマンド集
- `docs/DESIGN.md` - UI / UX 設計原則
- `docs/PRODUCT_SENSE.md` - プロダクト方針
- `docs/QUALITY_SCORE.md` - 品質基準
- `docs/RELIABILITY.md` - 再現性と障害耐性
- `docs/SECURITY.md` - セキュリティ原則

## 今後さらに改善するなら

今回の基盤改善に加えて、さらに進めるなら次を優先します。

1. OpenAPI 生成を CI に組み込み、契約差分を PR で検出する
2. `ResultStore` に registry 活用・manifest キャッシュや比較 API を追加する
3. Docker ベースの統合検証を CI で常時実行する
4. Python の成果物生成を段階的に DB または明示 manifest 中心へ移行する

バックテスト結果は過去条件に基づくものであり、将来の成績を保証するものではありません。
