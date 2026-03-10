# ARCHITECTURE

目的
- 本ドキュメントはプロジェクト全体のアーキテクチャとドメイン構成、パッケージ階層を示し、開発者が「どこに何を書くべきか」を判断するための基準を提供します。

システム構成（概要）
- python/: バックテスト、スクリーニング、データ処理、run manifest / registry を持つコア層（CLI 実行、CSV/PNG 出力）
- backend/: FastAPI ベースの API 層。python の出力ディレクトリを読み込み、フロントに JSON と charts (data:image/png;base64,...) を返す責務。
- frontend/: React + TypeScript 表示層（計算ロジック禁止）。API からのデータを表示するのみ。
- electron-launcher.js: デスクトップ起動用ラッパー（必要に応じて）。
- output/: python 側が生成する結果（backtest の出力フォルダ、charts/*.png, trades.csv 等）。
- docs/: 開発ドキュメント群。[docs/DOCUMENTATION_SYSTEM.md](docs/DOCUMENTATION_SYSTEM.md) を入口に、索引から必要な深さへ段階的にたどる。

責務分離
- python/: データ取得、処理、戦略ロジック、バックテスト実行、run manifest / registry、PNG/CSV 等のアーティファクト生成。
  - 変更時は必ず TDD（RED→GREEN→REFACTOR）で進め、外部 API はテストでモックする。
- backend/: API 層として出力ファイルを読み取り HTTP API に変換する。フロントが期待する契約（/api/backtest/latest で base64 PNG, /api/backtest/ohlc?ticker=... で OHLC JSON）を保持。
- frontend/: 受け取った契約をそのまま表示。計算は一切行わず、チャート表示（CandlestickChart 等）の実装は表示ロジックに限定する。

データフロー
1. python バックテストが output/backtest/... に結果（charts/*.png, trades.csv, ticker_stats.csv, ohlc.json 等）と `run_manifest.json` を出力し、`registry.json` を更新する。
2. backend/services/result_store.py と result_loader.py が出力フォルダと manifest を走査して、フロント用の charts / summary / run metadata を生成する。
3. フロントは /api/backtest/latest を取得し、charts の base64 PNG を背景に、/api/backtest/ohlc を使って lightweight-charts（または Plotly フォールバック）でローソク足を重ねて描画。

主要モジュールと役割（ファイル例）
- python/
  - experiments/models.py: run spec / metrics / artifacts / manifest の軽量モデル定義。
  - experiments/store.py: `run_manifest.json` と `registry.json` の保存責務。
  - backtest/data_preparation.py: データ取得後の前処理・指標付与をまとめる。
  - backtest/result_artifacts.py: trades / trade_log / ticker_stats の保存責務。
  - backtest/ticker_charts.py: PNG（ローソク足）生成、図のレイアウトとマーカー描画（mplfinance 等）。
  - scripts/: CLI ラッパー。引数検証と Fail Fast を行う。
- backend/
  - api/backtest.py: /latest, /ohlc 等のエンドポイント実装。
  - services/result_store.py: backtest run の探索と manifest 付き metadata 解決。
  - services/result_loader.py: output を走査し API 用オブジェクトを作る（期間フィルタ等のロジックをここに実装）。
- frontend/
  - src/components/CandlestickChart.tsx: bgImage と OHLC を合成して表示するコンポーネント（ズーム機能は一時的にコメントアウトする運用ルール）。
  - src/components/TopBottomPurchaseCharts.tsx: ダッシュボード用のラッパー。CandlestickChart へマーカー等を渡す。
- docs/
  - docs/design-docs/STRATEGY.md: 売買ロジックの仕様（必ずここを正とする）。
  - [COMMAND.md](COMMAND.md): 開発者向け操作コマンド集（WSL 特有コマンドは統合済み）。
  - ARCHITECTURE.md: （本ファイル）

ドキュメントと編集ルール
- ドキュメント全体の入口と役割分担は [docs/DOCUMENTATION_SYSTEM.md](docs/DOCUMENTATION_SYSTEM.md) を参照すること。
- 戦略ロジックの変更は `docs/design-docs/STRATEGY.md` を同時に更新すること。
- 実行手順・検証コマンドの変更は [COMMAND.md](COMMAND.md) を更新すること。
- 索引ファイルと生成ドキュメントの鮮度は `python scripts/check_docs.py` と `python scripts/doc_gardening.py` で検証・更新する。

作業時の判断基準（どこに書くか）
- コードの挙動・アルゴリズム変更 → python/ 内の該当ファイル + docs/design-docs/STRATEGY.md
- API 仕様変更 → backend/api/*.py と型定義、さらに frontend の受け口コンポーネント
- 表示ロジック・UI → frontend/src/components/ に実装。
- 開発手順・コマンド → [COMMAND.md](COMMAND.md)
- 設計思想やモジュール全体の責務 → [ARCHITECTURE.md](ARCHITECTURE.md)
- ドキュメント構造と運用ルール → [docs/DOCUMENTATION_SYSTEM.md](docs/DOCUMENTATION_SYSTEM.md)

運用上の注意点
- 出力ファイル（output/）は下流でのみ参照する。上流は下流のファイルフォーマットに依存しない。
- `run_manifest.json` は backend / frontend / 将来の比較 UI が共有する軽量な run 契約とする。
- 再現性重視：未来データ参照（look-ahead）は厳禁。
- テストは高速に、ネットワーク依存はモックする。

付録: 重要ファイルの短い参照
- frontend/src/components/CandlestickChart.tsx — チャート合成と表示の中心。
- backend/api/backtest.py — フロントとの契約を定義する場所。
- python/backtest/ticker_charts.py — PNG を生成するロジック。
- backend/services/result_loader.py — output を API 用に変換する責務。
