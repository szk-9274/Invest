# localhost visualization 改善提案

## 目的

localhost 可視化の初回イテレーションで追加したダッシュボード/詳細チャートを次の反復で改善するため、観点別の候補を整理する。

## 今回の到達点

- `/dashboard` に KPI 概要、条件比較、実験一覧テーブルを追加した
- `/dashboard/analysis` に equity / drawdown / signal events の詳細可視化を追加した
- backend の `summary` / `visualization` 契約を frontend と同期した

## 改善提案

### UX

- ダッシュボード上部に「現在選択中の run」「期間」「戦略名」を固定表示し、一覧スクロール中でも文脈が切れないようにする
- 実験一覧テーブルにソート、フィルタ、検索を追加し、比較対象をすばやく絞れるようにする
- モバイルでは KPI と比較カードの優先順位を見直し、比較パネルをアコーディオン化して視線移動を減らす

### チャート

- signal events に加えて signal strength の連続系列を保持し、閾値超過帯や保有期間のハイライトを重ねる
- run 間比較として、equity curve の重ね描き、relative return、drawdown overlap を切り替えられるようにする
- 分布比較用に trade PnL histogram、holding days の box plot、ticker ごとの scatter matrix を追加する

### パフォーマンス

- `plotly.js` の chunk が大きいため、詳細チャートを route 単位またはカード単位でさらに遅延読み込みする
- 長い時系列は backend で downsampling したサマリ系列も返し、初期表示のメモリ使用量を抑える
- `visualization` JSON を run ごとにキャッシュし、CSV からの再計算を避ける

### データモデル

- `run_manifest.json` に universe、ticker_count、parameter set name、parameter snapshot summary を追加し、フロントの一覧/比較表示をより明確にする
- `visualization` に OHLC overlay 用の price series、signal strength series、annotations を追加して契約を拡張する
- `headline_metrics` と `summary` の責務差を README と schema で明示し、命名規約を固定する

### テスト

- `BacktestDashboard.e2e.test.tsx` に比較 UI と詳細時系列のアサーションを追加する
- visualization JSON の schema regression test を backend 側に追加する
- 代表 fixture でスクリーンショット比較を入れ、見た目の崩れを検出しやすくする

### アクセシビリティ / 国際化 / ダークモード

- テーブルとチャートに aria-label / summary を追加し、キーボードで比較対象を切り替えられるようにする
- 日本語固定文言として残している `Experiment List` などを段階的に i18n キーへ寄せる
- 既存の明色カード中心 UI に対し、ダークモードトークンとコントラスト検証を追加する

### 運用

- artifact の肥大化対策として、古い run の圧縮・ローテーションルールを README と CLI に追加する
- CI で `export_frontend_contracts` の drift と frontend build を可視化ジョブとして固定する
- fixture-backed E2E を PR 必須チェックに昇格し、localhost 可視化の退行を検出する
