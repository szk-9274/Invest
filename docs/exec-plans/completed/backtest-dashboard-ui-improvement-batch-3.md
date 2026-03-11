# 実装計画: バックテストダッシュボード UI 改善バッチ 3

- フェーズ: localhost 可視化改善 Phase 4
- プラン: バックテストダッシュボード UI 改善バッチ 3
- 責任者: Copilot
- 目的: バックテストダッシュボード周辺のヘッダー整理、情報重複解消、固定レイアウト解除、インタラクティブチャート読込失敗修正、固定年次結果の再配置、著名トレーダー戦略の日本語化・視覚改善、既存 issue 整理を一括で実施する。
- issue 連携: `#59 Improve localhost visualization iteration 2`、`#61 Follow up dashboard improvements after mobile strategy rollout`
- 進捗: planning

## 前提
- `frontend/src/pages/BacktestDashboard.tsx` がヘッダー、ルートタブ、選択中 run サマリー、リロード操作をまとめて管理している。
- `frontend/src/pages/BacktestRunPage.tsx` に概要/KPI パネルと固定年次結果パネルが存在し、`frontend/src/hooks/useBacktestDashboardState.ts` が 2020/2021 固定年次結果を別読み込みしている。
- `frontend/src/components/BacktestVisualizationPanel.tsx` と `frontend/src/components/useLazyPlotComponent.ts` がインタラクティブチャートの描画と Plotly 遅延読込を担っており、ここが Task 4 の主調査対象になる。
- `frontend/src/pages/TraderStrategiesPage.tsx` と `frontend/src/locales/ja.json` に英語残りがあり、著名トレーダー戦略の表示改善はここを中心に行う。
- `#59` と `#61` は今回タスクと関連するが、現時点では包括的な改善提案 issue であり、今回の実装範囲が fully covered になった時点でクローズ可否を判定する。

## 変更・作成するファイル
- 更新候補: `frontend/src/App.tsx`, `frontend/src/App.i18n.test.tsx`
- 更新候補: `frontend/src/pages/BacktestDashboard.tsx`, `frontend/src/pages/BacktestDashboard.test.tsx`
- 更新候補: `frontend/src/pages/BacktestRunPage.tsx`, `frontend/src/pages/BacktestRunPage.test.tsx`
- 更新候補: `frontend/src/pages/BacktestAnalysisPage.tsx`, `frontend/src/pages/BacktestAnalysisPage.test.tsx`
- 更新候補: `frontend/src/pages/TraderStrategiesPage.tsx`, `frontend/src/pages/TraderStrategiesPage.test.tsx`
- 更新候補: `frontend/src/components/BacktestStatus.tsx`, `frontend/src/components/BacktestStatus.test.tsx`
- 更新候補: `frontend/src/components/BacktestVisualizationPanel.tsx`, `frontend/src/components/BacktestVisualizationPanel.test.tsx`
- 更新候補: `frontend/src/components/useLazyPlotComponent.ts`, `frontend/src/components/useLazyPlotComponent.test.tsx`
- 更新候補: `frontend/src/hooks/useBacktestDashboardState.ts`, 関連 hook / API / fixture test
- 更新候補: `frontend/src/locales/ja.json` と必要なら `frontend/src/locales/en.json`
- 更新候補: `docs/exec-plans/active/backtest-dashboard-ui-improvement-batch-3.md`, `docs/exec-plans/active/index.md`, `docs/generated/doc-inventory.md`

## 実装内容
- 1. バックテストダッシュボードのヘッダーから大見出しを除去し、グローバルナビのブランド表示を画面文脈に応じて動的切り替えする。
- 2. ヘッダー右側の操作を日本語状態表示 + 小型リロードアイコンへ置き換え、既存 `handleLoadLatest` と整合する操作性を保つ。
- 3. 実行管理タブから概要/KPI パネルを削除し、情報の正本を解析結果タブへ寄せる。
- 4. 選択中 run / 期間 / 戦略 / プロファイルのバーから sticky 固定を外し、通常スクロール内レイアウトへ変更する。
- 5. インタラクティブチャートの読込失敗を RED で再現し、`DetailTimeSeries` 相当の表示導線と `InteractiveChart` 相当の描画導線を確認した上で修正する。
- 6. 固定年次結果パネルを削除し、2020年・2021年の年次結果を実行管理タブの `Experiment List` 内へ他の run と同形式で統合する。
- 7. 著名トレーダー戦略の英語残りを排除し、漫画風・イラスト風のローカル SVG アバターへ変更する。
- 8. GitHub issue #59 / #61 の本文と今回実装範囲を照合し、実装完了後に解決済み issue をクローズする。

## 影響範囲
- frontend の dashboard / run / analysis / strategies 各画面
- Plotly 遅延読込とフォールバック UI
- ダッシュボード state orchestration (`useBacktestDashboardState`)
- i18n 文言とページ間ナビゲーション
- frontend 単体テスト、E2E、ドキュメント索引、GitHub issue 運用

## 実装ステップ
### Task 1: issue 整理と RED 準備
- [ ] `#59` / `#61` の重複観点と今回スコープ外観点を整理する
- [ ] Task 1〜6 をカバーする RED テストを追加し、現状失敗を再現する
- [ ] Task 4 の読込失敗をテストと実画面で再現し、根本原因を特定する

### Task 2: ヘッダー・ナビ・状態表示整理
- [ ] `BacktestDashboard` の大見出しを削除する
- [ ] `App.tsx` のブランド表示を `/dashboard` 系では「バックテストダッシュボード」へ切り替える
- [ ] `BacktestStatus` を日本語状態表示へ整え、ヘッダー右側に小型リロードアイコンを配置する

### Task 3: 実行管理タブと固定情報バーの簡素化
- [ ] `BacktestRunPage` から概要/KPI パネルを削除する
- [ ] `BacktestDashboard` の選択中情報バーから sticky を外し、通常レイアウト化する
- [ ] 既存の run 管理操作やルート遷移を壊さないようテストを更新する

### Task 4: インタラクティブチャート修正
- [ ] `useLazyPlotComponent` の import / register / error handling を点検する
- [ ] `BacktestVisualizationPanel` のデータガードと描画条件を見直す
- [ ] フォールバックだけでなく正常描画ケースをテストで担保する

### Task 5: 固定年次結果の再配置
- [ ] `useBacktestDashboardState` の pinned annual results 取得ロジックを見直す
- [ ] `BacktestRunPage` の固定年次結果パネルを削除する
- [ ] 2020年・2021年結果を実行管理タブの `Experiment List` へ他の run と同形式で統合する

### Task 6: 著名トレーダー戦略の日本語化・視覚改善
- [ ] `TraderStrategiesPage` の名称・説明・補助文・件数表示を日本語化する
- [ ] 絵文字ベース表示をローカル SVG の漫画風アバターへ置き換える
- [ ] `ja.json` に残る英語ラベルを洗い出して日本語へ統一する

### Task 7: 検証・docs・issue クローズ
- [ ] `npm --prefix frontend run test:coverage` を通し、coverage 80%以上を確認する
- [ ] `npm run test:e2e` と `npm run build` を通す
- [ ] `python scripts/doc_gardening.py && python scripts/check_docs.py` を通す
- [ ] #59 / #61 が今回の変更で解消済みならクローズする

## 注意点
- Task 5 の移動先は、ユーザー確認により解析結果タブではなく実行管理タブの `Experiment List` へ統合する方針とする。
- 外部アセットは追加せず、著名トレーダーアバターはローカル実装の SVG / CSS で完結させる。
- 本番コードでは英語ラベルの残存を避けるが、テスト名やコード識別子まで無理に翻訳しない。
- 既存 backend / contracts を壊す変更が必要になった場合は、frontend 修正と同じバッチで型・テストを更新する。
