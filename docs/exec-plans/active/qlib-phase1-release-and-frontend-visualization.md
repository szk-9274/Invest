# 実装計画: qlib phase-1 リリース整理と localhost 可視化初回イテレーション

- タイトル: qlib phase-1 リリース整理と localhost 可視化初回イテレーション
- 責任者: Copilot
- 進捗: reviewed-pending-commit
- 対象ブランチ: `feature/localhost-visualization`

## 目的
`feature/localhost-visualization` で中断していた localhost 可視化の初回イテレーションを再開し、backend が既に持つ run metadata / headline metrics / visualization 契約を frontend のダッシュボードと詳細チャートへ接続する。既存の Python / backend / frontend の責務分離を守りつつ、実験一覧・条件比較・主要 KPI・詳細系列表示の基盤を整える。

## 現状サマリー
- Python 側では `python/experiments/`、`run_manifest.json`、`registry.json` を使う軽量 recorder 構成が追加されている。
- backend 側では `backend/services/result_store.py` が `headline_metrics` を組み立て、`backend/schemas/backtest.py` が `visualization`（equity / drawdown / signal events）を含む契約を定義している。
- frontend 側では `BacktestRunPage.tsx` / `BacktestAnalysisPage.tsx` を中心に既存のダッシュボードがあるが、`frontend/src/api/generated/contracts.ts` が古く、実験一覧テーブル・条件比較・新しい詳細時系列表示は未着手の状態が残っている。
- 今回の再開では、既存画面を壊さずに「実験一覧」「条件比較」「主要指標概要」「詳細チャート」へ拡張する。

## 変更・作成対象ファイル
### 既存変更のレビュー/安定化
- `python/main.py`
- `python/backtest/engine.py`
- `python/backtest/data_preparation.py`
- `python/backtest/result_artifacts.py`
- `python/experiments/*`
- `backend/api/backtest.py`
- `backend/services/result_store.py`
- `backend/services/result_loader.py`
- `backend/schemas/backtest.py`
- `frontend/src/api/generated/contracts.ts`
- `frontend/src/pages/BacktestRunPage.tsx`
- `frontend/src/pages/BacktestAnalysisPage.tsx`
- 既存の関連 test 一式

### localhost 可視化の初回実装候補
- `frontend/src/App.tsx`
- `frontend/src/api/backtest.ts`
- `frontend/src/hooks/` 配下の新規 hook
- `frontend/src/pages/` 配下のダッシュボード/詳細画面
- `frontend/src/components/` 配下の実験一覧、条件比較、KPI カード、詳細チャート、ジョブ履歴関連コンポーネント
- `frontend/src/styles/` 配下の関連スタイル
- 必要に応じて `backend/api/backtest.py` と schema / tests

### ドキュメント
- `README.md`
- `ARCHITECTURE.md`
- `COMMAND.md`
- `docs/references/design-ref-llms.md`
- 必要なら `docs/design-docs/` または `docs/product-specs/` の追加記録
- 改善提案用の issue またはドキュメント

## 実装内容
1. 既存 phase-1 差分の自己レビューを行い、命名・責務・エラー処理・ロギング・ドキュメント整合の観点で不足を補う。
2. 既存の build/test/docs コマンドで最低限のスモークテストを実施し、成功ログを残す。
3. feature ブランチを push し、`feature/qlib-inspired-architecture` -> `develop` PR を作成する。
4. PR 本文に What/Why、影響範囲、実行手順、テスト結果、既知制約を記載する。
5. CI が通ったら `develop` にマージする。
6. `develop` -> `main` の release PR を作成し、CHANGELOG 相当のリリースノートを含める。
7. フロントでは実験一覧テーブル、条件比較、主要 KPI、詳細チャートの骨格を追加し、PC/スマホの基本レスポンシブを確保する。
8. フロントが直接描画できる JSON 形式の時系列契約を整理し、必要なら backend から供給する。
9. artifacts の保存先・パス規約を README に明記する。
10. 参考資料の URL、採用理由、再解釈内容、反映箇所を `docs/references/design-ref-llms.md` に追記する。
11. 実装後は改善提案を issue または docs にまとめ、ask_user で次アクションを確認する。

## 影響範囲
- データ取得/結果保存: manifest と artifacts の読み取り・表示契約
- 条件/特徴量: 既存 phase-1 metadata 表示と比較 UI の土台
- バックテスト: 既存結果の後方互換性維持
- 評価: 年率、IR、MDD などの指標表示面
- ローカル表示: dashboard/detail page、JSON 契約、レスポンシブ UI

## 実装ステップ
- [x] Phase 1 / Task 1: 既存差分の自己レビューと影響範囲要約をまとめる
- [x] Phase 1 / Task 2: frontend のデータ I/O 契約（generated contracts / API helper）を backend 現行契約へ合わせる
- [x] Phase 1 / Task 3: 実験一覧テーブル、主要 KPI、条件比較のダッシュボード UI を TDD で追加する
- [x] Phase 1 / Task 4: 詳細チャート画面に equity / drawdown / signal / trade detail 表示を TDD で追加する
- [x] Phase 1 / Task 5: frontend build/test と必要な backend test を実行して GREEN を確認する
- [x] Phase 1 / Task 6: README と `docs/references/design-ref-llms.md` を更新し、改善提案を記録する
- [x] Phase 1 / Task 7: 実装レビュー結果を反映し、次アクションを `ask_user` で確認する

## 注意点
- `main` へのマージは必ず PR レビュー経由で実施する。
- 既存のバックテスト/分析ロジックを壊さない。
- 既存 UI と API 契約の後方互換性をできる限り維持する。
- references 追記では、参考元の丸写しではなく再解釈内容を明記する。
- 完了後は `docs/exec-plans/completed/` へ移動し、索引は `python scripts/doc_gardening.py` で更新する。
