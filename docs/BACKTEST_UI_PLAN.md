# Backtest UI 改善 実装計画

作成日: 2026-03-07

目的
- スマホでも使いやすいバックテスト UI を構築し、バックテストの進行状況と結果を直感的に確認できるようにする。

適用範囲
- フロントエンド（frontend/*）の UI/ルーティング/コンポーネントの改修。
- テスト更新（ユニット／UI テスト）とローカライズ（ja/en）の微調整。

前提・注意点
- 現行バックエンドはジョブの進捗（%）を明示的に返していないため、フロントでは「状態（queued/running/...）」「経過時間」「最新ログプレビュー」を表示する設計とする。
  - 進捗% 表示を要する場合はバックエンド API の拡張が必要。
- 既存の RunPanel / BacktestDashboard / ChartGallery / CandlestickChart 等を再利用して最小差分で実装する。

実装の全体方針（推奨順）
1. タブ整理（Backtest タブを UI から削除）
2. 実行状態表示（ヘッダに常時確認できるステータスを追加）
3. Backtest Dashboard の UI 分割（Run / Results）
4. チャート改善（Candlestick 背景 + マーカー、フルスクリーン表示、ズーム）

タスク詳細

- Task 1: 未使用バックテストタブの整理
  - 変更箇所:
    - frontend/src/App.tsx
    - frontend/src/locales/ja.json, frontend/src/locales/en.json
    - 必要に応じてテスト修正 (frontend/src/App.i18n.test.tsx)
  - 変更内容:
    - ナビゲーションから未使用の「Backtest」リンクを削除（現在は `/` にリンクしており Home と重複している）。
    - ルーティング自体に分岐はないため、リンク削除で対応。必要なら route 削除を別タスクで検討。

- Task 2: バックテスト実行状況の可視化
  - 追加ファイル:
    - frontend/src/hooks/useActiveJob.ts (新規)
    - frontend/src/components/BacktestStatus.tsx (新規)
  - 変更箇所:
    - frontend/src/pages/BacktestDashboard.tsx
    - frontend/src/components/RunPanel.tsx (状態共有のため小修正)
  - 実装要点:
    - createJob 実行時に返る job_id を localStorage に保存（key: invest_active_job_id など）してページ間で復元可能にする。
    - useActiveJob フックで getJob / getJobLogs をポーリング（2s）して activeJob と logs を保持、経過時間を計算する。
    - BacktestStatus をアプリのヘッダ（BacktestDashboard の上部）に表示し、常に現在のジョブ状態・経過時間・簡易ログ（最新 N 行）を見せる。
    - バックエンドに progress フィールドが無ければ % 表示は行わない（代替: ステップ推定やログ解析は別タスク）。

- Task 3: バックテスト画面の UI 改善（スマホ最適化）
  - 変更箇所:
    - frontend/src/pages/BacktestDashboard.tsx
    - CSS 調整（同ファイル内の style か共通 CSS）
  - 実装要点:
    - 上位にタブ（Run / Results）を導入。モバイルでは Run を優先して全幅表示、Results はチャート優先レイアウトにする。
    - Run タブ: Strategy / Timeframe / Run ボタン / Execution Log（RunPanel を再利用）
    - Results タブ: Summary / Performance chart / Trade list / Statistics（既存の BacktestSummary / ChartGallery / TradeTable を活用）

- Task 4: チャート表示改善（TradingView 風）
  - 変更箇所:
    - frontend/src/components/CandlestickChart.tsx
    - frontend/src/components/ChartGallery.tsx
    - frontend/src/components/TopBottomPurchaseCharts.tsx
  - 実装要点:
    - CandlestickChart の Plotly トレースを有効化し、ローソク足を背景表示してその上に entry/exit マーカーをプロットする（現在 buildCandlestickTraces は既に実装済み）。
    - クリック/タップでフルスクリーンモーダルを開き、react-plotly.js を遅延ロードして pinch-zoom（モバイル）を有効化する。
    - 既存の ChartGallery の modal を活用してチャート画像と Plotly ビューを切り替え可能にする。

影響ファイル（主なもの）
- frontend/src/App.tsx
- frontend/src/pages/BacktestDashboard.tsx
- frontend/src/components/RunPanel.tsx
- frontend/src/components/BacktestSummary.tsx
- frontend/src/components/TradeTable.tsx
- frontend/src/components/TopBottomPurchaseCharts.tsx
- frontend/src/components/ChartGallery.tsx
- frontend/src/components/CandlestickChart.tsx
- frontend/src/hooks/useActiveJob.ts (新規)
- frontend/src/components/BacktestStatus.tsx (新規)
- frontend/src/locales/*.json (ja/en) とテストファイル

テスト・ビルド手順（検証）
1. ユニットテスト: npm --prefix frontend run test（該当コンポーネントのテストを更新）
2. ビルド: npm --prefix frontend run build
3. ローカル動作確認: npm --prefix frontend run dev（UI 上で Run → Dashboard を操作）

リスクと対応
- 進捗% がバックエンドに無い場合、UI 上のプログレスバーは誤解を招くため実装しない。必要ならバックエンド側の API 拡張を依頼する。
- 既存テストが nav の文言や DOM に依存している場合、テスト修正が必要。
- Plotly の導入はバンドルサイズに影響するため遅延ロード（動的 import）で対応する。

成果物
- セッションの plan.md（本ファイル）
- session DB の todos に実装タスクを登録（実施済み）

次のアクション
- この計画で実装を進めてよいか確認を得る（ユーザー承認後、実装ブランチを作成して作業開始）。
