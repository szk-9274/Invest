# 実装計画: qlib phase-1 リリース整理と localhost 可視化初回イテレーション

- タイトル: qlib phase-1 リリース整理と localhost 可視化初回イテレーション
- 責任者: Copilot
- 進捗: planned
- 対象ブランチ: `feature/qlib-inspired-architecture` -> `develop` -> `main`

## 目的
`feature/qlib-inspired-architecture` にある phase-1 の変更を安全に自己レビュー・検証・PR・マージし、続けて localhost で成果物を可視化できるダッシュボード/詳細チャートの初回実装を開始する。既存の Python / backend / frontend の責務分離を守りつつ、実験一覧・条件比較・主要 KPI・詳細系列表示の基盤を整える。

## 現状サマリー
- Python 側では `python/experiments/`、`run_manifest.json`、`registry.json` を使う軽量 recorder 構成が追加されている。
- backend 側では `backend/services/result_store.py` と `result_loader.py` が run metadata を読み出し、`backend/api/backtest.py` が frontend 契約へ変換している。
- frontend 側では `BacktestRunPage.tsx` / `BacktestAnalysisPage.tsx` を中心に既存のダッシュボードがあり、Plotly と生成済み TypeScript 契約を利用している。
- 今回の初回イテレーションでは、既存画面を壊さずに「実験一覧」「条件比較」「主要指標概要」「詳細チャート」へ拡張する。

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
- [ ] Phase 1 / Task 1: 既存差分の自己レビューと影響範囲要約をまとめる
- [ ] Phase 1 / Task 2: ベースラインの build/test/docs チェックを実行し、スモークログを残す
- [ ] Phase 1 / Task 3: 必要な修正を TDD で反映し、feature ブランチを push する
- [ ] Phase 1 / Task 4: feature -> develop PR を作成し、CI 緑を確認して develop にマージする
- [ ] Phase 1 / Task 5: develop -> main の release PR を作成し、リリースノートを添える
- [ ] Phase 2 / Task 6: フロントの情報設計とデータ I/O 契約を固める
- [ ] Phase 2 / Task 7: 実験一覧・比較・KPI・詳細チャートの最小 UI を実装する
- [ ] Phase 2 / Task 8: frontend/backend の関連テストを追加・更新して GREEN にする
- [ ] Phase 2 / Task 9: README / references / 必要 docs を更新する
- [ ] Phase 3 / Task 10: 実装レビュー・最終検証・改善提案の記録を完了する

## 注意点
- `main` へのマージは必ず PR レビュー経由で実施する。
- 既存のバックテスト/分析ロジックを壊さない。
- 既存 UI と API 契約の後方互換性をできる限り維持する。
- references 追記では、参考元の丸写しではなく再解釈内容を明記する。
- 完了後は `docs/exec-plans/completed/` へ移動し、索引は `python scripts/doc_gardening.py` で更新する。
