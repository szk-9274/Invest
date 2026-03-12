# 実装計画: ダッシュボード軽量化と保守性改善バッチ 2

- フェーズ: localhost 可視化改善 Phase 3
- プラン: ダッシュボード軽量化と保守性改善バッチ 2
- 責任者: Copilot
- 目的: issue `#61` を起点に、dashboard / strategies / visualization 周辺のパフォーマンス、保守性、テストカバレッジ、UX を次段階へ改善する。
- issue 連携: `#61 Follow up dashboard improvements after mobile strategy rollout`
- 進捗: planning

## 前提
- mobile UI 改善、pinned annual results、trader-inspired strategies、lightbox は main に反映済み。
- frontend build では `plotly.min` chunk の大きさに warning が出ており、初回表示コストの削減余地がある。
- strategy metadata は python / backend / frontend で保持されており、今後の profile 追加時に重複更新が発生しやすい。

## 変更・作成するファイル
- 更新候補: `frontend/src/components/BacktestVisualizationPanel.tsx`, `frontend/src/components/ChartGallery.tsx`, `frontend/src/components/ExperimentListTable.tsx`, `frontend/src/components/RunPanel.tsx`
- 更新候補: `frontend/src/pages/BacktestDashboard.tsx`, `frontend/src/pages/TraderStrategiesPage.tsx`, `frontend/src/hooks/useBacktestDashboardState.ts`, `frontend/src/components/useLazyPlotComponent.tsx`
- 更新候補: `frontend/src/App.tsx`, `frontend/src/api/backtest.ts`, `vite.config.ts` または chunk 分割に関係する build 設定
- 更新候補: `backend/api/backtest.py`, `backend/services/result_store.py`, `backend/schemas/backtest.py`
- 更新候補: `python/main.py`, `python/experiments/models.py`, `python/experiments/store.py`, `python/config/params.yaml`
- 追加候補: strategy profile 共通 metadata helper、filter persistence helper、追加 E2E / fixture regression tests
- 更新候補: `docs/design-docs/STRATEGY.md`, performance / UI fallback に関する design docs, `README.md`

## 実装内容
- 1. Plotly と詳細可視化の遅延読み込み・chunk 分割を見直し、dashboard 初回表示を軽量化する。
- 2. `RunPanel` / `ExperimentListTable` / sticky summary / mobile fallback の責務を分離し、再利用可能な小さい component / hook へ整理する。
- 3. strategy profile metadata の重複管理を減らし、python / backend / frontend で同じ定義を安全に参照できる形を検討する。
- 4. experiment list の filter / sort / search 状態を URL もしくは永続状態へ保持し、再訪時の操作性を上げる。
- 5. `/dashboard/strategies`、pinned annual results、lightbox keyboard 操作、strategy filter を E2E / regression tests で補強する。
- 6. run manifest / backend schema / frontend contracts における `strategy_name` / `rule_profile` / pinned period の責務を文書化する。

## 影響範囲
- frontend の dashboard / analysis / strategies 各画面
- build chunk 構成と lazy-loading 導線
- strategy metadata 契約と run manifest 保存形式
- backend の run 選択 API と fixture テスト
- docs の strategy / UI fallback / performance 運用

## 実装ステップ
### Task 1: 現状計測と RED 準備
- [ ] build warning の発生箇所と bundle size の主要因を計測する
- [ ] strategy metadata の重複箇所を洗い出す
- [ ] filter persistence / lightweight loading / E2E 不足に対する失敗テストを追加する

### Task 2: パフォーマンス改善
- [ ] Plotly 周辺の lazy load と chunk 分割を見直す
- [ ] モバイル時の signal / chart fallback 表示を軽量な既定値へ寄せる
- [ ] 初回表示で不要な fetch / render を減らす

### Task 3: UI / 状態管理の保守性改善
- [ ] Experiment List の controls を小さい部品へ抽出する
- [ ] sticky summary と mobile accordion のロジックを整理する
- [ ] filter / sort / search 状態の URL または local persistence を実装する

### Task 4: strategy metadata 契約改善
- [ ] strategy profile 定義の共有方法を決める
- [ ] python / backend / frontend の metadata を整合させる
- [ ] run manifest / schema / docs に責務差分を反映する

### Task 5: テストとドキュメント
- [ ] `/dashboard/strategies`、pinned annual results、lightbox keyboard、filter persistence の E2E / regression tests を追加する
- [ ] `npm --prefix frontend run test:coverage`、`npm run test:e2e`、`npm run build`、必要な backend/python tests を通す
- [ ] `python scripts/doc_gardening.py && python scripts/check_docs.py` でドキュメント整合性を確認する

## 注意点
- 既存の mobile UX 改善を損なわず、軽量化のために機能を後退させない。
- strategy profile は今後追加される前提で、定義の増殖を抑える設計を優先する。
- URL 永続化を採用する場合は、既存 routing と i18n query の共存を確認する。
