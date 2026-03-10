# セッションログ: Qlib inspired architecture adaptation

保存日時: 2026-03-10T02:02:49Z
作成者: Copilot

## 概要
- 既存の Invest に対して、Qlib のうち相性の良い思想だけを軽量に導入した。
- 全面移植ではなく、既存の yfinance / ルールベース / FastAPI / React / Electron 導線を維持したまま、責務分離・再現性・比較検証性を高めた。

## 実施内容（要点）
1. 保全
   - `backup/pre-qlib-adaptation-20260310` ブランチと `pre-qlib-adaptation-20260310` タグを現行 HEAD に作成。
   - 作業ブランチ `feature/qlib-inspired-architecture` を作成して以後の変更を分離。
2. Python 基盤整理
   - `python/experiments/` を追加し、`RunSpec` / `BacktestRunManifest` / `ExperimentStore` を実装。
   - 各バックテスト run に `run_manifest.json` を保存し、`python/output/backtest/registry.json` に run 一覧を集約するようにした。
   - `python/backtest/data_preparation.py` でデータ取得後の前処理責務を分離。
   - `python/backtest/result_artifacts.py` で trades / trade_log / ticker_stats 保存責務を分離。
   - `python/main.py` は run metadata と parameter snapshot を保存する導線へ更新。
3. パラメータ明文化
   - `python/config/params.yaml` に `experiment` セクションを追加し、`name` / `strategy_name` / `rule_profile` / `tags` を明示化。
4. backend / frontend 追従
   - backend は `run_manifest.json` を読み、run 一覧と詳細 API に `run_metadata` を含めるようにした。
   - frontend は run list / analysis header で metadata を表示できるようにした。
5. ドキュメント更新
   - README / ARCHITECTURE / COMMAND / STRATEGY / references を更新し、軽量 recorder 構造と参考情報の採否を追記。

## 採用した考え方
- workflow を config-driven にし、run ごとの parameter snapshot を保存する。
- data / signal / backtest / record を小さく分離し、疎結合化する。
- MLflow や外部 API を使わず、ローカル JSON ベースで experiment / recorder 相当を実装する。

## 採用しなかった考え方
- RD-Agent や外部 LLM API 前提の構成。
- MLflow tracking server 常設。
- Qlib 独自データフォーマットや深層学習基盤の全面導入。

## 主要変更ファイル（抜粋）
- `python/experiments/models.py`
- `python/experiments/store.py`
- `python/backtest/data_preparation.py`
- `python/backtest/result_artifacts.py`
- `python/main.py`
- `python/backtest/engine.py`
- `backend/services/result_store.py`
- `backend/api/backtest.py`
- `frontend/src/pages/BacktestRunPage.tsx`
- `frontend/src/pages/BacktestAnalysisPage.tsx`
- `docs/references/design-ref-llms.md`

## 期待される次の拡張
1. `registry.json` を使った実験一覧 API / 比較 API の追加。
2. `run_label` や比較条件編集をローカル UI から投入する入力導線の追加。
3. CPU 軽量 scorer を `strategy_name` / `rule_profile` と並ぶ metadata として差し替え可能にする。
