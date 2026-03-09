# 実装計画: ダッシュボード改善バッチ 1

- タイトル: ダッシュボード改善バッチ 1
- 責任者: Copilot
- 目的: バックテスト画面分離後の改善として、性能・テスト・hook 責務分離・共通スタイル整理・終了理由 i18n 正規化を 1 から 5 の優先順で実装する。
- 進捗: implemented-and-reviewed

## 変更・作成するファイル
- 更新候補: `frontend/src/pages/BacktestAnalysisPage.tsx`, `frontend/src/components/TopBottomPurchaseCharts.tsx`, `frontend/src/components/CandlestickChart.tsx`, `frontend/vite.config.ts`
- 更新候補: `frontend/src/hooks/useBacktestDashboardState.ts`, `frontend/src/pages/BacktestRunPage.tsx`, `frontend/src/pages/BacktestAnalysisPage.tsx`, `frontend/src/components/TradeTable.tsx`, `frontend/src/locales/en.json`, `frontend/src/locales/ja.json`
- 更新候補: 既存テスト群 (`frontend/src/pages/*.test.tsx`, `frontend/src/components/*.test.tsx`, `frontend/src/hooks/*.test.tsx`) と必要な新規テスト
- 作成候補: `frontend/src/hooks/useBacktestJobManagement.ts`, `frontend/src/pages/BacktestRunPage.test.tsx`, `frontend/src/pages/BacktestAnalysisPage.test.tsx`, `frontend/src/styles/dashboard-cards.css`, 必要に応じた補助 hook / utility

## 実装内容
- 1. Plotly/チャート領域の遅延読込を見直し、分析画面で可視時ロードへ寄せて初期表示を軽くする。
- 2. `BacktestRunPage` と `BacktestAnalysisPage` の単体テストを追加し、現在の統合寄りテストを補強する。
- 3. `useBacktestDashboardState` からジョブ管理責務を切り出し、hook の責務を整理する。
- 4. 実行画面・解析画面で重複しているカード系スタイルを共通 CSS へ集約する。
- 5. 終了理由マッピングを i18n 主体へ寄せ、翻訳キーと UI 表示ロジックの一貫性を高める。

## 影響範囲
- バックテスト解析画面の初期表示性能
- バックテスト関連 hook とページ構成
- TradeTable の表示ロジックとローカライズ
- frontend テスト構成とカバレッジ
- 共通スタイル運用

## 実装ステップ
- [x] 1 の性能改善方針を確定し、可視時ロードの差分を実装する
- [x] 2 のページ単体テストを追加し、既存テストとの役割分担を整理する
- [x] 3 の hook 責務分離を行い、既存画面との接続を保つ
- [x] 4 のカード系スタイルを共通化し、既存見た目を維持する
- [x] 5 の終了理由ロジックを i18n ベースへ整理し、テストで担保する
- [x] frontend の既存検証コマンドで動作を確認する

## 注意点
- 順番はユーザー指定どおり 1 → 5 を維持し、前段の変更で後段を壊さないようにする
- 速度改善では不要な機能削除ではなく、分析画面の体感改善を優先する
- hook 分離後も `/dashboard/run` と `/dashboard/analysis` の state 共有を壊さない
- i18n 正規化では既存 raw 値との互換性を残しつつ、表示ロジックを単純化する

## 実施結果
- 分析画面のチャートセクションを `useDeferredVisibility` で可視時ロードにし、`CandlestickChart` から `plotly.js-dist-min` の静的画像生成経路を除去した。
- `BacktestRunPage.test.tsx`、`BacktestAnalysisPage.test.tsx`、`useBacktestJobManagement.test.tsx` を追加してページ責務とジョブ管理の検証を補強した。
- ジョブ管理を `useBacktestJobManagement.ts` へ分離し、polling effect の依存配列も review で調整した。
- `dashboard-cards.css` を追加して run / analysis のカード系スタイルを共通化した。
- `TradeTable` は locale の raw exit reason キーを優先参照する実装へ整理した。
- 検証は `npm --prefix frontend run test:coverage && npm --prefix frontend run build` で完了した。
