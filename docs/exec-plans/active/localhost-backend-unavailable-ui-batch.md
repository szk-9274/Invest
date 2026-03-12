# 実装計画: localhost backend unavailable UI 改善バッチ

- フェーズ: localhost 可視化改善 Phase 5
- プラン: localhost で backend が未起動または到達不能なときに、汎用 fetch エラーではなく専用の案内 UI を表示する
- 責任者: Copilot
- 目的: frontend を backend より先に起動した開発者が、`/api/*` 到達不能時に generic error message だけを読むのではなく、backend 未起動と次アクションを即座に理解できる体験へ改善する
- 前提:
  - `devinit.sh` と local command は rename 耐性を持つ形へ修正済み
  - 現状の dashboard は `loadBacktestListError` / `loadBacktestResultsError` などの汎用文言で `String(err)` をそのまま表示している
  - localhost では backend 停止時に Vite proxy 由来の 500 や `Failed to fetch` が混在し、原因が分かりづらい
- 進捗: planning

## 変更・削除・作成するファイル
- 更新候補: `frontend/src/hooks/useBacktestDashboardState.ts`
- 更新候補: `frontend/src/pages/BacktestDashboard.tsx`
- 更新候補: `frontend/src/locales/ja.json`, `frontend/src/locales/en.json`
- 更新候補: `frontend/src/pages/BacktestDashboard.test.tsx`
- 更新候補: `frontend/src/pages/BacktestDashboard.e2e.test.tsx` または hook / component テスト
- 作成候補: `frontend/src/components/BackendUnavailableState.tsx`
- 更新候補: `docs/exec-plans/active/localhost-backend-unavailable-ui-batch.md`

## 実装内容
- backend 到達不能を判定するための frontend 側 error classification を整理する
- localhost / Vite proxy / `Failed to fetch` / 500 proxy failure を backend unavailable として扱う条件を決める
- dashboard 上に専用の offline / unavailable state を出し、backend 未起動の説明、再試行導線、起動ヒントを表示する
- 既存の generic error 表示は、本当にその他のアプリケーションエラーだけに残す
- RED -> GREEN -> REFACTOR で回帰テストを追加し、localhost UX の退行を防ぐ

## 影響範囲
- dashboard 初期表示時のエラー UX
- `useBacktestDashboardState` の error state 設計
- i18n 文言と通知表示
- localhost 開発時の初動説明
- dashboard 関連ユニット / 統合 / E2E テスト

## 実装ステップ
- [ ] Task 1: 現状の error 導線を整理し、backend unavailable の判定条件と表示要件を確定する
- [ ] Task 2: backend unavailable UI に対する失敗テストを追加して RED を作る
- [ ] Task 3: error classification と専用 UI を最小差分で実装して GREEN にする
- [ ] Task 4: 文言・レイアウト・再試行導線を整理し、generic error と責務を分離する
- [ ] Task 5: `npm --prefix frontend run test:coverage`、必要な dashboard 関連 E2E / build を実行して検証する
- [ ] Task 6: 差分レビュー後、ユーザー確認を待つ

## 注意点
- backend unavailable 判定を広げすぎて本来の 500 アプリケーションエラーを隠さない
- localhost 専用の案内に寄せつつ、production で誤解を生まない文言にする
- 既存 Notification と競合する二重エラー表示を避ける
- 新しい UI が mobile / desktop の両方で読めることを意識する
