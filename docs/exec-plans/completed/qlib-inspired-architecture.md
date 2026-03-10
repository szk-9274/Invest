# 実装計画: Qlib inspired architecture adaptation

- タイトル: Qlib inspired architecture adaptation
- 責任者: Copilot
- 目的: 既存の yfinance・ルール判定・バックテスト・ローカル表示資産を維持しつつ、Qlib のうち相性が良い設計思想だけを軽量に取り込み、責務分離・再現性・比較検証性・将来の可視化拡張性を高める。
- 進捗: planned
- 保全: `backup/pre-qlib-adaptation-20260310` ブランチと `pre-qlib-adaptation-20260310` タグを `c6b15da` に作成済み。作業ブランチは `feature/qlib-inspired-architecture`。

## 現状調査サマリー
- データ取得: `python/data/fetcher.py` の `YahooFinanceFetcher` が yfinance 取得・ローカルキャッシュ・リトライを担う。
- 前処理/特徴量: `python/analysis/indicators.py` が SMA/BB/RSI/MACD などを計算し、`screening/screener.py` と `backtest/engine.py` の両方から呼ばれている。
- シグナル/ルール: `python/analysis/stage_detector.py` が Stage2、`python/backtest/entry_condition.py` が日次エントリー、`config/params.yaml` がしきい値の正本。
- バックテスト: `python/backtest/engine.py` がデータ取得、特徴量計算、ルール評価、執行、診断、結果保存まで広く抱えており責務が集中している。
- 評価/結果保存: `python/backtest/performance.py`、`trade_logger.py`、`ticker_analysis.py` があるが、実行条件スナップショットや比較用メタデータは弱い。
- ローカル表示: `backend/services/result_store.py` と `result_loader.py` が `python/output/backtest/` を走査し、`frontend/src/hooks/useBacktestDashboardState.ts` とページ群が表示する。
- 設定/実行方法: `python/main.py`、FastAPI、Vite、Electron、`just dev` が入口。設定は `params.yaml`・CLI 引数・`INVEST_OUTPUT_DIR` に分散。

## 参考にする Qlib 思想
- 採用候補 1: data / feature / strategy / backtest / record を疎結合に分ける。
- 採用候補 2: 実行条件を config-driven にし、run ごとの parameter snapshot を保存する。
- 採用候補 3: experiment / recorder に相当する軽量メタデータ管理をローカルファイルで実装する。
- 採用候補 4: 将来の軽量モデル導入に備えて signal provider / scorer の拡張点を先に切る。
- 今回不採用: RD-Agent、外部 LLM API 前提、MLflow 常時依存、Qlib 独自データフォーマット全面移行、深層学習中心設計。

## 変更・作成するファイル
- 更新候補: `python/main.py`, `python/config/params.yaml`, `python/backtest/engine.py`, `python/backtest/performance.py`, `python/backtest/trade_logger.py`, `python/backtest/ticker_analysis.py`
- 更新候補: `backend/services/result_store.py`, `backend/services/result_loader.py`, `backend/schemas/backtest.py`, `backend/api/backtest.py`, 必要な backend tests
- 更新候補: `frontend/src/api/backtest.ts`, `frontend/src/hooks/useBacktestDashboardState.ts`, `frontend/src/pages/BacktestAnalysisPage.tsx`, `frontend/src/pages/BacktestRunPage.tsx`, 関連 tests
- 更新候補: `README.md`, `ARCHITECTURE.md`, `COMMAND.md`, `docs/design-docs/STRATEGY.md`, `docs/references/design-ref-llms.md`
- 作成候補: `python/experiments/` 配下の run spec / manifest / registry 関連モジュール、`python/backtest/` 配下の artifact 保存補助モジュール、必要な unit/integration tests、必要なら `docs/design-docs/` の軽量設計メモ

## 実装内容
- 1. バックテスト実行の入力条件を `run spec` として正規化し、`start/end/tickers/benchmark/rule profile/output path` を1つの構造にまとめる。
- 2. `params.yaml` のルール・しきい値を追いやすく整理し、Stage / Entry / Exit / Risk / Backtest / Experiment の境界を明確にする。
- 3. `BacktestEngine` から、少なくとも `データ準備`, `ルール評価`, `評価指標集計`, `結果保存` の責務を補助モジュールへ段階抽出する。
- 4. 各 run の `manifest` を保存し、実行日時・対象期間・銘柄数・使用パラメータ・評価指標・出力ファイル一覧・比較用タグを残す。
- 5. backend が manifest を読めるようにし、一覧 API / 詳細 API に比較・可視化しやすいメタデータを含める。
- 6. frontend では大規模 UI 追加は避けつつ、将来のローカルホスト比較表示に使える run metadata を保持・表示しやすい状態へ寄せる。
- 7. 将来の CPU 軽量モデル導入に向け、ルールベース signal と学習ベース score を差し替えやすい拡張ポイントだけを整理する。

## 影響範囲
- Python バックテスト CLI の実行経路
- 出力ディレクトリの保存物とメタデータ構造
- backend の run 一覧・詳細取得 API
- frontend のバックテスト実行/分析画面
- ドキュメント、テスト、今後のローカルホスト比較機能の土台

## 実装ステップ
- [ ] Phase 1 / Task 1: 既存テスト・ビルドを実行して現状ベースラインを確認する
- [ ] Phase 1 / Task 2: `python/experiments/` に run spec・manifest・registry の軽量基盤を追加し、実行条件/成果物/指標の保存形式を定義する
- [ ] Phase 2 / Task 3: `python/main.py` と `backtest/engine.py` を段階整理し、データ準備・評価・保存の責務を分割する
- [ ] Phase 2 / Task 4: ルール/パラメータ構造を整理し、比較検証しやすい profile/snapshot の形へ寄せる
- [ ] Phase 3 / Task 5: backend に manifest 読み取りと run metadata 応答を追加し、比較・一覧用途の契約を整える
- [ ] Phase 3 / Task 6: frontend を最小変更で追従させ、将来の比較 UI に必要な metadata を読み回せる状態にする
- [ ] Phase 4 / Task 7: README / ARCHITECTURE / COMMAND / STRATEGY / references を更新し、参考情報と採否を明記する
- [ ] Phase 4 / Task 8: backend / frontend / e2e / docs 検証を再実行し、working-memory 更新まで完了する

## 注意点
- 既存の yfinance・ルールベース・簡易バックテスト・ローカル UI は壊さず、差分の意図が追える小さな変更に分ける。
- 実験管理はローカル完結の軽量 JSON/YAML ベースを優先し、外部サービス依存は導入しない。
- 出力物は backend / frontend が読みやすい構造を意識し、将来の実験一覧・比較表示にそのままつなげる。
- ルールの可読性・比較容易性を優先し、深いモデル導入は拡張ポイント整備までに留める。
