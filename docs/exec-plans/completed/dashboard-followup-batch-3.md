# 実装計画: ダッシュボード改善バッチ 3

- フェーズ: バックテストダッシュボード改善 Phase 5
- プラン: Issue #63 に基づく metadata / artifact / chart preview 改善
- 責任者: Copilot
- 目的: トレーダー拡張時の重複更新を減らし、chart preview の責務を明確化し、review ノイズの大きい build artifact 運用を見直しつつ、UI 回帰を E2E で補強する。
- issue 連携: `#63 Follow up trader dashboard metadata, artifact, and chart preview design`
- 進捗: planning

## 前提
- `TraderStrategiesPage` / `TraderAvatar` / `strategyProfileLocalization` で trader metadata が複数箇所に分散している。
- `CandlestickChart` は preview 画像を `/api/backtest/latest` から推測して取得しており、run 選択済みコンテキストと責務が混在している。
- `renderer-dist/` は frontend build のたびに大きな差分を発生させやすい。
- 現在の E2E は analysis 初期表示中心で、strategies / summary / rank badge / icon button の回帰を十分に拾えていない。

## 変更・作成するファイル
- 更新候補: `frontend/src/utils/strategyProfileLocalization.ts`
- 更新候補: `frontend/src/components/TraderAvatar.tsx`
- 更新候補: `frontend/src/pages/TraderStrategiesPage.tsx`
- 更新候補: `frontend/src/components/CandlestickChart.tsx`
- 更新候補: `frontend/src/api/backtest.ts`
- 更新候補: `frontend/src/pages/BacktestDashboard.e2e.test.tsx`
- 更新候補: `backend/api/backtest.py`
- 更新候補: `backend/services/result_store.py`
- 更新候補: `backend/schemas/backtest.py`
- 更新候補: `.gitignore`, build/packaging 関連設定, `package.json`, `COMMAND.md`
- 更新候補: `docs/design-docs/STRATEGY.md` または chart preview / artifact 運用に関する design doc
- 追加候補: `frontend/src/domain/traderProfiles.ts` のような共通 manifest
- 追加候補: chart preview contract を表す helper / schema / test

## 実装内容
- 1. trader metadata を 1 つの manifest に集約し、表示文言・画像キー・fallback を共通利用できるようにする。
- 2. chart preview の取得契約を見直し、ticker 名推測ではなく run context ベースで安定的に取得できる導線へ寄せる。
- 3. `renderer-dist/` の更新運用を整理し、通常のソース変更レビューで build artifact ノイズを減らす。
- 4. strategies / summary / chart card の主要 UI を E2E で補強する。
- 5. 画像 placeholder を正式 asset に置き換えやすい形へ整え、読み込み・失敗時の扱いを明確化する。

## 影響範囲
- frontend の strategy metadata 管理と trader avatar 表示
- backend の chart preview API / schema / result selection
- build artifact と配布物の運用
- dashboard E2E coverage
- docs の design / command / exec-plan inventory

## 実装ステップ
### Task 1: RED - 契約と回帰の失敗テストを用意
- [ ] trader metadata の単一正本化を前提とした unit test を追加する
- [ ] chart preview を run context から解決する失敗 test を backend / frontend に追加する
- [ ] strategies / summary / rank badge / expand icon の E2E を追加して失敗させる

### Task 2: GREEN - metadata / chart preview / artifact 運用を実装
- [ ] trader metadata manifest を作成し、localization と avatar をそこへ寄せる
- [ ] chart preview API / response contract を明示化し、`CandlestickChart` の推測ロジックを縮小する
- [ ] `renderer-dist/` の追跡方針を整理し、必要なら packaging 手順を調整する

### Task 3: REFACTOR - 責務整理
- [ ] strategy/trader 表示ロジックの重複を減らし、小さい helper に分ける
- [ ] chart preview と selected run state の責務境界を明確にする
- [ ] build artifact 更新の責務を source change と分離できるかを整理する

### Task 4: 検証とドキュメント
- [ ] `npm --prefix frontend run test:coverage`、`npm run test:e2e`、`npm run build` を通す
- [ ] 必要な backend/python tests を通す
- [ ] `python/.venv/bin/python3 scripts/doc_gardening.py && python/.venv/bin/python3 scripts/check_docs.py` を通す

## 注意点
- 既存の Minervini baseline 導線を壊さない。
- chart preview 契約変更時は frontend/backend の互換性を同時に保つ。
- build artifact 方針変更はリリース手順への影響を必ず確認する。
