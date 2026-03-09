# Invest

Invest は、Python の分析・バックテスト基盤、FastAPI の API 層、React のフロントエンドを組み合わせた株式スクリーニング／バックテスト用ワークスペースです。過去データに対する戦略検証、生成済み成果物の参照、ダッシュボード上での結果確認を一つのリポジトリで扱えます。

## 概要

このプロジェクトでは主に次のことができます。

- Python CLI からスクリーニングやバックテストを実行する
- 実行結果を `python/output/` 配下へ保存する
- FastAPI からバックテスト結果、ジョブ状態、関連データを API として取得する
- React UI でサマリ、チャート、トレード一覧、ジョブ進捗を表示する
- 必要に応じて Electron ベースのデスクトップ実行フローを使う

## アーキテクチャ

責務はレイヤごとに分かれています。

- `python/`: データ処理、スクリーニング、バックテスト実行、成果物生成
- `backend/`: `python/output/` を読み取り、HTTP API として公開
- `frontend/`: API のレスポンスを描画する React + TypeScript UI
- `electron-launcher.js` とルート `package.json`: Electron 向けの起動・パッケージング
- `docs/`: 設計、コマンド、品質、運用ルール

データフローは次のとおりです。

1. Python コマンドが `python/output/backtest/...` に成果物を出力する
2. backend がその出力を読み、API レスポンスへ変換する
3. frontend が API を通じて結果を描画する

## ディレクトリ構成

```text
.
├── python/                 # スクリーニング、バックテスト、設定、出力、テスト
├── backend/                # FastAPI アプリ、API ルーター、サービス、API テスト
├── frontend/               # React アプリ、API クライアント、ページ、コンポーネントテスト
├── docs/                   # 設計資料、コマンド集、品質・運用ドキュメント
├── devinit.sh              # tmux ベースの開発環境起動スクリプト
├── justfile                # よく使う開発コマンド
├── electron-launcher.js    # Electron 起動ラッパー
└── package.json            # Electron 向けルートスクリプト
```

## 前提環境

推奨環境は以下です。

- Python 3.9 以上
- Node.js 18 以上
- npm
- just
- tmux
- lazygit

補足:

- `just dev` は `devinit.sh` を経由して tmux セッションを立ち上げます。
- Python 依存は `python/requirements.txt` から導入します。
- フロントエンド依存は `frontend/package.json` で管理されています。
- ルート `package.json` は Electron ワークフロー用です。

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

### 3. フロントエンド依存を導入

```bash
npm --prefix frontend install
```

### 4. Electron 用のルート依存を導入（必要な場合のみ）

```bash
npm install
```

補足: ルートの Electron ビルド系スクリプトは現状そのままでは整っておらず、利用前に `tsconfig.json` を含む設定の見直しが必要です。

## 起動方法

### 推奨: 開発環境をまとめて起動

```bash
just dev
```

`devinit.sh` に定義された tmux ベースの開発環境が起動します。

### tmux セッションを停止

```bash
just stop
```

### ログを確認

```bash
just logs
```

## Python ワークフロー

Python コマンドを実行する前に仮想環境を有効化してください。

```bash
cd python
source .venv/bin/activate
```

主な実行例:

```bash
python main.py --mode backtest
python main.py --mode backtest --start 2023-01-01 --end 2023-12-31
python main.py --mode backtest --no-charts
python main.py --mode chart --ticker AAPL --start 2023-01-01 --end 2023-12-31
python scripts/update_tickers_extended.py --min-market-cap 5000000000
```

設定は主に `python/config/` を参照し、成果物は `python/output/` に出力されます。

## バックエンド API

Python 仮想環境を有効化したうえで、リポジトリルートから起動します。

```bash
cd python
source .venv/bin/activate
cd ..
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

主なエンドポイント:

- `GET /` - API の基本情報
- `GET /health` - ヘルスチェック
- `POST /api/backtest/run` - バックテストジョブを投入
- `GET /api/backtest/latest` - 最新バックテスト結果一式を取得
- `GET /api/backtest/results` - トレードログと銘柄統計を取得
- `GET /api/backtest/tickers` - 損益上位／下位銘柄を取得
- `GET /api/backtest/list` - 利用可能なバックテスト一覧を取得
- `GET /api/charts/{ticker}` - 銘柄チャート用データを取得
- `GET /api/charts/{ticker}/trades` - 売買マーカーを取得
- `POST /api/jobs` - バックグラウンドジョブを作成
- `GET /api/jobs/{job_id}` - ジョブ状態を取得
- `GET /api/jobs/{job_id}/logs` - ジョブログを取得
- `POST /api/jobs/{job_id}/cancel` - ジョブの停止を要求

起動確認例:

```bash
curl http://localhost:8000/health
```

## フロントエンド

開発サーバーの起動:

```bash
npm --prefix frontend run dev -- --host 0.0.0.0 --port 3000 --strictPort
```

主な画面ルート:

- `/` - バックテスト実行と上位／下位銘柄確認のホーム画面
- `/home` - ランディングページ
- `/dashboard` - サマリ、チャート、トレード一覧、ジョブ操作を備えたダッシュボード
- `/chart/:ticker` - 個別銘柄画面

フロントエンドのビルド:

```bash
npm --prefix frontend run build
```

フロントエンドのテスト:

```bash
npm --prefix frontend run test -- --run
npm --prefix frontend run test:coverage
```

## Electron ワークフロー

ルートには Electron 向けスクリプトが含まれていますが、現時点ではルート `npm run build` が `tsconfig.json` の入力設定不足で失敗するため、そのままでは安定運用できません。Electron を本格利用する場合は、まずルートの TypeScript / build 設定を整備してください。

Electron が不要な場合は、この領域を使わず Python / backend / frontend のみで開発できます。

## テストと品質確認

Python 側:

```bash
cd python
source .venv/bin/activate
cd ..
pytest backend/tests -q
```

ショートカット:

```bash
just test
just lint
just fmt
```

フロントエンド側:

```bash
npm --prefix frontend run build
npm --prefix frontend run test -- --run
```

## 参考ドキュメント

より詳細な背景は次のドキュメントを参照してください。

- `ARCHITECTURE.md` - システム構造と責務分離
- `COMMAND.md` - 手動実行コマンド集
- `docs/DESIGN.md` - UI / UX 設計原則
- `docs/PRODUCT_SENSE.md` - プロダクト価値と信頼性方針
- `docs/QUALITY_SCORE.md` - テスト・品質基準

## 開発上の原則

このリポジトリでは次を重視しています。

- 決定的な処理と look-ahead の禁止
- 分析層、API 層、表示層の責務分離
- 再現可能な出力と明示的な実行コマンド
- 実装作業に対するテストファースト

バックテスト結果は過去条件の再現であり、将来の成績を保証するものではありません。

## もしゼロから作り直すなら

現状の構成を活かしつつ、ゼロから再設計できるなら次の改善を優先します。

### 1. 分析層と API 層の契約を明確化する

- 出力ファイル依存を薄め、永続化モデルまたはバージョン付き契約へ寄せる
- OpenAPI を公開し、フロントエンドの型と API 契約を一致させる
- 長時間ジョブの実行管理をリクエスト処理からさらに分離する

### 2. ローカル再現性を上げる

- Docker / Docker Compose を導入し、ワンコマンドで起動できるようにする
- Linux、macOS、Windows、WSL で差分の少ないセットアップ導線を整える
- 起動時に設定値と依存関係を自己診断できるようにする

### 3. テストを縦断的に強化する

- Python 生成物 -> API 読み込み -> frontend 描画までの E2E を追加する
- Python / frontend のカバレッジを CI で可視化し、基準未達を検知する
- `trade_log.csv`、`ticker_stats.csv`、チャート payload の契約テストを整備する

### 4. 現在のプロダクト面の曖昧さを減らす

- どの画面が完成済みで、どこが暫定実装かを明示する
- エラー表示、再試行、ジョブ進捗表示の UX を統一する
- API と UI の失敗時メッセージを一貫させる

### 5. データ処理と性能の戦略を見直す

- 出力ディレクトリ読み取りだけに依存せず、キャッシュや結果ストアを導入する
- 大きなチャートデータやトレードデータを段階的に読み込めるようにする
- ジョブ実行時間、API レイテンシ、成果物更新時刻の観測性を高める

### 6. 保守性を上げる

- 大きい Python エントリポイントを小さなサービス単位へ分割する
- デバッグ用スクリプトを本流から切り離す
- README、COMMAND、実行スクリプトのコマンド定義を同期しやすい形に寄せる
