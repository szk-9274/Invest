## 1. Invest プロジェクト概要

このリポジトリは、ルールベースの株式スクリーニングおよびバックテストを行うためのツール群を収めたプロジェクトです。コアのバックテスト・スクリーニングは python/ に実装され、実行結果（CSV やチャート画像）を backend の API（FastAPI）が読み取り、frontend の React + TypeScript アプリで可視化します。設計方針としてはデータパイプライン（Stage1 / Stage2 / Backtest）を採用し、再現性・決定性を最優先にしています。

## 2. このプロジェクトでできること

- 大量銘柄に対するテクニカルスクリーニング（Stage2）
- ルールベースのバックテスト（エントリー・エグジットのシミュレーション）
- バックテスト結果のチャート生成（PNG）と CSV 出力
- FastAPI 経由でのバックテスト結果提供（チャートは base64 Data URI）
- React ダッシュボードでの結果表示・ログ確認・コマンド実行（Python Command Runner）
- スクリプトによる銘柄リスト更新や各種ユーティリティ実行

## 3. システム構成

- python/: バックテストやスクリーニング本体、スクリプト類（CLI 実行）
  - エントリポイント: main.py（--mode で stage2 / backtest / chart 等を指定）
  - 出力例: python/output/backtest/backtest_YYYY-MM-DD_to_YYYY-MM-DD_TIMESTAMP/
    - trades.csv, ticker_stats.csv, trade_log.csv, charts/*.png など

- backend/: FastAPI による API 層
  - python 側の出力を読み、JSON を返す（charts は data:image/png;base64,... 形式）
  - 提供 API 例: /api/backtest/list, /api/backtest/latest, /api/backtest/results/{timestamp}

- frontend/: React + TypeScript（Vite ビルド）
  - ダッシュボードでバックテスト一覧・サマリ・チャート・トレードテーブルを表示
  - 環境変数: REACT_APP_API_URL（API のベース URL を上書き可能）

- optional: Electron 関連ファイル（デスクトップ版の開発用スクリプトが含まれる）

データフロー: python バックテスト実行 -> output ディレクトリへ CSV/PNG 出力 -> backend が読み込み JSON で配信 -> frontend が表示

## 4. クイックスタート

前提: Python と Node.js / npm がインストールされていること。

### 1) Python 環境の準備（Windows PowerShell の例）

```bash
cd /mnt/c/00_mycode/Invest/python
# 仮想環境作成（任意の名前、ここでは .venv を例示）
python -m venv .venv
# 仮想環境を有効化
source .venv/bin/activate
# 依存関係をインストール
pip install -r requirements.txt
```

注: プロジェクトで既に venv 名が使われている可能性があるため、環境名に合わせてパスを調整してください（例: source venv/bin/activate など）。

### 2) バックエンド起動

```bash
cd /mnt/c/00_mycode/Invest/backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

バックエンドは http://localhost:8000 で起動します（同一ネットワーク端末からはホストIP:8000 でもアクセス可能）。

### 3) フロントエンド起動

```bash
cd /mnt/c/00_mycode/Invest/frontend
npm install
npm run dev -- --host
```

フロントエンドは開発サーバで http://localhost:3000 に表示される想定です（同一ネットワーク端末からはホストIP:3000 でもアクセス可能、環境によりポートや設定が異なる場合があります）。

### 4) ブラウザでダッシュボードを開く

http://localhost:3000/dashboard

### 5. CLI の使い方 (主要コマンド例)

- Stage2（スクリーニング）:

```bash
cd /mnt/c/00_mycode/Invest/python
python main.py --mode stage2
python main.py --mode stage2 --with-fundamentals
```

- Backtest（バックテスト）:

```bash
cd /mnt/c/00_mycode/Invest/python
python main.py --mode backtest
python main.py --mode backtest --start 2023-01-01 --end 2024-01-01
python main.py --mode backtest --tickers AAPL,MSFT,NVDA
python main.py --mode backtest --no-charts  # チャート生成をスキップ
```

- Chart（個別チャート生成）:

```bash
python main.py --mode chart --ticker AAPL --start 2023-01-01 --end 2024-01-01
```

- スクリプト実行例（銘柄リスト更新など）:

```bash
python scripts/update_tickers_extended.py --min-market-cap 5000000000 --max-tickers 2000
```

- API 経由でジョブを作成する例（バックエンドの /api/jobs）:

```bash
curl -X POST http://localhost:8000/api/jobs -H "Content-Type: application/json" -d "{\"command\":\"backtest\",\"start_date\":\"2024-01-01\",\"end_date\":\"2024-12-31\"}"
```

### 6. ディレクトリ構成（概要）

- .github/                     : CI / Copilot 指示など
- backend/                     : FastAPI の API 層（app 起動）
- frontend/                    : React + TypeScript アプリ（Vite）
- python/                      : バックテスト / スクリーニング本体、scripts/
- docs/                        : 補足ドキュメント（存在する場合）
- tests/                       : テストコード（pytest 等）
- package.json                 : ルートの npm スクリプト（Electron など）
- electron-launcher.js         : Electron 起動補助
- vite.config.ts / tailwind.config.js : フロントエンド設定

### 7. ドキュメント一覧

- README.md       : 本ファイル（プロジェクト概要・導線）
- STRATEGY.md     : 売買ロジック、フィルタ条件、エントリー/エグジットの仕様（ロジック変更時は必ず参照/更新）
- COMMAND.md      : 開発時の起動コマンド、デバッグ手順、環境構築メモ
