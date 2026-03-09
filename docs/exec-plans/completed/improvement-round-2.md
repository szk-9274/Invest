# 改善提案ラウンド2の実装計画

## 変更・削除・作成するファイル
- frontend/src/pages/BacktestDashboard.tsx と関連テスト
- frontend/src/components/RunPanel.tsx / Home.tsx / TradeTable.tsx / BacktestForm.tsx / ChartGallery.tsx など act warning 対象のテスト群
- frontend/src/hooks/useActiveJob.ts と関連テスト
- backend/services/result_store.py / backend/api/backtest.py / backend/services/result_loader.py と関連テスト
- frontend/src/api/backtest.ts / frontend/src/api/generated/contracts.ts と必要な UI コンポーネント
- frontend/src/components/CandlestickChart.tsx / TopBottomPurchaseChart.tsx / TopBottomPurchaseCharts.tsx / frontend/vite.config.ts
- frontend/src/locales/*.json と必要なら docs/ARCHITECTURE.md / COMMAND.md / docs/FRONTEND.md / docs/QUALITY_SCORE.md
- docs/exec-plans/active/improvement-round-2.md

## 実装内容
1. 残っている React act warning を RED→GREEN で解消し、主要コンポーネントテストの決定性を上げる
2. backend の結果選択とエラーハンドリングを整理し、timestamp/period 解決の曖昧さを減らす
3. Plotly 読み込みをさらに軽量化し、巨大 chunk と描画待ちを抑える
4. pinned バックテストの UI/UX を改善し、固定表示の意図と複数 run の扱いを分かりやすくする

## 影響範囲
- frontend テスト安定性と非同期 state 更新
- backend の backtest 選択 API と契約
- frontend build の chunk 構成と表示性能
- dashboard の sidebar 表示とユーザー理解

## 実装ステップ
- [x] act warning を再現する失敗テストを追加し、対象箇所を洗い出す
- [x] warning 原因の非同期更新と timer/event 処理を修正して関連テストを通す
- [x] backend の結果選択ロジックと API エラー経路に失敗テストを追加する
- [x] selector/error handling を整理し、契約とテストを更新する
- [x] Plotly 軽量化の失敗検証または build 検証を追加する
- [x] dynamic import / chunk 構成 / fallback 表示を見直して build を通す
- [x] pinned 結果の UI 文言・補助表示・テストを更新する
- [x] backend / frontend / docs の関連検証を再実行する

## 実装結果メモ
- Plotly 読み込みを `react-plotly.js/factory` + `plotly.js-dist-min` に寄せ、対話表示時のみ lazy load するよう整理した
- frontend build では Plotly chunk が `plotly-core` 約 4.67 MB / gzip 1.42 MB まで縮小し、従来の巨大 vendor chunk より大幅に圧縮できた
- pinned 年次バックテストには補助説明文と `available_runs` 表示を追加し、固定結果と複数 run の関係を UI 上で明示した
- 検証は `pytest backend/tests -q`、`npm --prefix frontend run test:coverage`、`npm run build` を再実行して完了した

## 前提
- 改善はユーザー希望どおり 1 から順に進めるが、1 つのラウンド計画として連続実施する
- 既存の pinned 年次結果は保持し、ディレクトリ削除は行わない
- API 契約変更が生じる場合は generated contracts と frontend テストを同時更新する
