# 実装計画: バックテストダッシュボード追加 UI 変更

- フェーズ: バックテストダッシュボード改善 Phase 4
- プラン: トレーダー戦略タブと解析結果タブの UI 整理
- 責任者: Copilot
- 目的: 現行バックテストを Mark Minervini 戦略として明示しつつ、将来のトレーダー拡張に耐える UI / asset / docs 構成へ整理する。
- 進捗: completed

## 前提
- 現在のバックテストロジックは `docs/design-docs/STRATEGY.md` に記載された Minervini ベースである。
- `/dashboard/strategies` は strategy metadata を使ってトレーダー一覧を描画している。
- 解析結果タブは `BacktestAnalysisPage` と `BacktestSummary`、チャート群は `TopBottomPurchaseCharts` と `CandlestickChart`、トレード一覧は `TradeTable` が担当している。

## 変更・作成するファイル
- 更新候補: `frontend/src/pages/TraderStrategiesPage.tsx`
- 更新候補: `frontend/src/components/TraderAvatar.tsx`
- 更新候補: `frontend/src/pages/BacktestAnalysisPage.tsx`
- 更新候補: `frontend/src/components/BacktestSummary.tsx`
- 更新候補: `frontend/src/components/MetricCard.tsx`
- 更新候補: `frontend/src/components/TopBottomPurchaseCharts.tsx`
- 更新候補: `frontend/src/components/CandlestickChart.tsx`
- 更新候補: `frontend/src/components/TradeTable.tsx`
- 更新候補: `frontend/src/utils/strategyProfileLocalization.ts`
- 更新候補: `frontend/src/pages/TraderStrategiesPage.test.tsx`
- 更新候補: `frontend/src/pages/BacktestAnalysisPage.test.tsx`
- 更新候補: `frontend/src/components/TopBottomPurchaseCharts.test.tsx`
- 更新候補: `frontend/src/components/CandlestickChart.test.tsx`
- 更新候補: `frontend/src/components/TradeTable.test.tsx`
- 追加: `frontend/src/assets/traders/`
- 追加: `docs/design-docs/strategy-mark-minervini.md`
- 追加: `docs/design-docs/strategy-warren-buffett.md`
- 追加: `docs/design-docs/strategy-george-soros.md`
- 追加: `docs/design-docs/strategy-peter-lynch.md`
- 追加: `docs/design-docs/strategy-ray-dalio.md`

## 実装内容
- 1. 著名トレーダー戦略タブで `Mark Minervini` を既存バックテスト結果に結び付け、他トレーダーも同じ UI スロットで将来追加しやすい構造に整理する。
- 2. トレーダー選択 UI に顔画像を表示し、画像未取得時でも破綻しない placeholder 表示を用意する。
- 3. 解析結果タブの見出し文言を summary 系に変更し、サマリーカード内の loading / empty / text 配置を常時中央寄せに統一する。
- 4. Profit Factor カードの折り返し崩れを防ぐため、カード幅・ラベル表示・改行制御を見直す。
- 5. チャートカードから Period / Year 切り替え UI を削除し、上位カードに Top1〜TopN バッジ、拡大アイコンボタンを追加する。
- 6. トレード一覧テーブルをヘッダー・セルとも中央配置へ揃え、既存モバイルカード表示との整合も保つ。
- 7. 将来の戦略拡張用 design-doc を placeholder として追加し、後続で doc gardening 対象に載せる。

## 影響範囲
- バックテストダッシュボード内の `Trader Strategies` / `Analysis & Results` / chart gallery / trade table UI
- strategy profile の表示ロジックと Minervini の扱い
- frontend asset 読み込みと画像 fallback
- frontend unit test / page test
- docs design-doc inventory

## 実装ステップ
### Task 1: RED - 既存 UI 仕様差分の失敗テスト追加
- [ ] `TraderStrategiesPage` に Minervini 表示・顔画像表示・既存バックテスト紐付けの期待値を追加する
- [ ] `BacktestAnalysisPage` / `BacktestSummary` に summary 文言と中央配置の期待値を追加する
- [ ] `TopBottomPurchaseCharts` / `CandlestickChart` / `TradeTable` に期間切替削除、Top バッジ、拡大アイコン、中央配置の期待値を追加する

### Task 2: GREEN - UI 実装
- [ ] トレーダー画像 asset / placeholder を追加し `TraderAvatar` を画像優先の実装へ更新する
- [ ] `Mark Minervini = current backtest` として扱う導線を `TraderStrategiesPage` と strategy label 側へ反映する
- [ ] summary パネル文言、中央配置、Profit Factor 幅・nowrap を実装する
- [ ] chart panel の Period / Year selector を削除し、Top ランクバッジと icon expand button を実装する
- [ ] trade table の全セル中央配置を実装する

### Task 3: REFACTOR - 構造整理
- [ ] トレーダー metadata / avatar mapping を後続追加しやすい形へ整理する
- [ ] 重複しやすい className / label 生成を小さく整理し、既存画面を壊さない形で整える

### Task 4: ドキュメントと検証
- [ ] design-doc placeholder 5件を追加する
- [ ] `npm --prefix frontend run test:coverage`、`npm run test:e2e`、`npm run build` を実行して回帰確認する
- [ ] `python/.venv/bin/python3 scripts/doc_gardening.py && python/.venv/bin/python3 scripts/check_docs.py` で docs 整合性を確認する

## 注意点
- 既存 run API や backend の strategy 契約は壊さず、UI 上の扱いを Minervini へ寄せる。
- 画像が未投入でも UI が崩れないよう fallback を維持する。
- 解析結果タブの詳細時系列パネルとシグナルイベントパネルには不要な変更を入れない。

## 実施結果
- `Mark Minervini` 選択時は既存バックテスト結果を表示する導線へ変更した。
- トレーダー画像 placeholder asset と design-doc placeholder を追加した。
- summary 見出し、中央配置、Profit Factor 折り返し、チャート操作、テーブル中央揃えを反映した。
- `npm --prefix frontend run test:coverage && npm run test:e2e && npm run build && python/.venv/bin/python3 scripts/doc_gardening.py && python/.venv/bin/python3 scripts/check_docs.py` を通して回帰確認した。
