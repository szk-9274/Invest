# /home 用アセット収集・分類計画（metaplanet.jp/en）

更新日時: 2026-03-05T17:48:31+09:00（ヘッドレスキャプチャ実行結果を含む）

## 目的

- metaplanet.jp/en の見た目（Hero / Features / Logos / CTA）を参考に、当リポジトリの /home ページ用に必要なアセットを収集・分類し、実装計画に反映すること。

## Task2 STEP 1: PLAN（/home UI 実装）

### 変更箇所（予定）

- frontend/src/App.tsx
  - `/home` ルート追加、既存 `/` との導線整理。
- frontend/src/pages/Home.tsx（既存）
  - 現在の backtest 操作用 UI を保持したまま、metaplanet.jp/en 準拠の Hero / Features / Logos / CTA セクションを追加。
- frontend/src/pages/Home.test.tsx（既存）
  - Hero 見出し、CTA、ロゴ群、レスポンシブ崩れ防止に関する最小テストを追加。
- docs/PLAN/assets-licenses.md
  - 利用アセットの出典・ライセンス・保存先を記録。

### 影響範囲

- 影響あり: `/home` の表示。
- 影響なし: `/dashboard` の機能、backend API 仕様。

### 受け入れ基準

- `/home` で Hero / Features / Logos / CTA が表示される。
- 主要ビューポート（モバイル/デスクトップ）でレイアウト崩れがない。
- 画像・ロゴなど外部アセットは `docs/PLAN/assets-licenses.md` に記録済みのもののみ使用する。

### 参照アセット・参照 URL

- https://metaplanet.jp/en
- docs/PLAN/assets/home_en_full.png
- docs/PLAN/assets/home_en_resources.json
- docs/PLAN/assets/home_en_resources_perf.json

### STEP 3: REVIEW（Task2 実装後）

- 機能: `/home` に Hero / Features / Logos / CTA セクションを実装し、`/dashboard` への導線を確認。
- アクセシビリティ: セクションに見出し・ラベル（`aria-label`）を付与し、リンク/ボタンのキーボード操作を維持。
- パフォーマンス: 画像の直接導入は行わず、背景は CSS グラデーションで実装して初期読み込み負荷を抑制。
- ライセンス: 外部ロゴは placeholder 表示に留め、`docs/PLAN/assets-licenses.md` の `pending` 状態を維持。
- 検証:
  - `npm --prefix frontend run test`
  - `npm --prefix frontend run build`
  - `docs/PLAN/assets/home_task2.png`（/home スクリーンショット）

## 実行概要（実績）

- 手法: Playwright によるヘッドレスレンダリングでページを読み込み、フルページスクリーンショットとネットワークリソース一覧を取得。
- 生成物（docs/PLAN/assets）:
  - home_en_full.png — フルページスクリーンショット（約907 KB）
  - home_en_resources.json — ネットワークリソース（生ログ、約57 KB）
  - home_en_resources_perf.json — performance.getEntries に基づく資源一覧（約9 KB）

## 収集方針（短く）

1. まずは UI 再現に必要な「Hero」「ロゴ」「主要イラスト/アイコン」「パートナーロゴ」「フォント」を高優先で収集する。
2. 取得したアセットはライセンス確認を行い、許可があれば低解像度のプレビューあるいは原寸を private asset host に保存する。リポジトリへ直接コミットするのは最終的な権利クリア後に限定する。
3. CSS/JS は実装参考として参照するが、ビルド済みファイルやチャンクをそのままコミットしない（実装は自前で再構築する）。

## アセット分類（ヘッドレスキャプチャ結果からの抜粋）

- ヒーロー / 背景画像（優先度: 高）
  - https://metaplanet.jp//images/planets-hero.jpeg（大きさ: 約215 KB、Hero 背景）
  - 参考: Supabase 上の home-page.jpg（外部 CDN 参照）

- ロゴ（優先度: 高）
  - https://metaplanet.jp/images/logos/light/_012.svg
  - https://metaplanet.jp/images/logos/dark/_012.svg
  - https://metaplanet.jp/images/logos/light/_015.svg
  - https://metaplanet.jp/images/logos/dark/_015.svg

- パートナー / 掲載ロゴ（優先度: 中）
  - https://metaplanet.jp/images/partners/bitcoin.jp-white.svg
  - https://metaplanet.jp/images/partners/bm-japan-white.svg
  - https://metaplanet.jp/images/partners/planetgear-white.svg
  - 一部は /_next/image を経由した PNG（自動最適化）もあり

- アイコン類（優先度: 低→中）
  - https://metaplanet.jp/images/companies/linkedin-icon.svg
  - https://metaplanet.jp/images/companies/youtube-icon.svg

- フォント（優先度: 高、要ライセンス確認）
  - https://metaplanet.jp/_next/static/media/24f6ebe2756575bd-s.p.woff2
  - https://metaplanet.jp/_next/static/media/36966cca54120369-s.p.woff2
  - https://metaplanet.jp/_next/static/media/9a4ee768fed045da-s.p.woff2
  - https://metaplanet.jp/_next/static/media/b7bd7951037de757-s.p.woff2
  - https://metaplanet.jp/_next/static/media/d3ebbfd689654d3a-s.p.woff2
  - https://metaplanet.jp/_next/static/media/92eeb95d069020cc-s.woff2

- CSS（実装参考）
  - https://metaplanet.jp/_next/static/css/a8d12fb7c765706d.css
  - https://metaplanet.jp/_next/static/css/cf2af83f588f3be0.css
  - https://metaplanet.jp/_next/static/css/fd9ae5657ac7550b.css

- JS チャンク（実装参考 / 動的ロード）
  - /_next/static/chunks/（多数） — 例: 4bd1b696-....js, main-app-d41d56f7....js, 7174-d5586f6b....js（大きめの chunk あり）

- その他（埋め込み / API）
  - https://metaplanet.jp/_vercel/insights/script.js
  - https://metaplanet.jp/_vercel/speed-insights/script.js
  - https://admin.metaplanet.jp/api/events/promoted?domain=metaplanet.jp

## 優先度付きアクション（短期）

1. Hero と Header ロゴを優先してダウンロード（ローカル検証用の低解像度コピーを docs/PLAN/assets/originals に保存）。
2. フォントはライセンス情報を確認し、OSS/商用の可否を判定（ライセンス不明は使用しない）。
3. パートナー/掲載ロゴは使用許諾を確認。許可が取れない場合はモノクロのプレースホルダや自作アイコンで代替。
4. CSS/JS は直接コミットせず、見た目を再現するためのデザイン仕様（カラー/タイポ/間隔）を抽出して実装。
5. 取得・決定したアセットについては docs/PLAN/assets-licenses.md を作成し、出典・ライセンス・保存場所を記録。

## 次のステップ（確定）

1. `docs/PLAN/assets-licenses.md` を作成し、今回参照するアセットのライセンス状態を記録する。
2. ライセンス未確定アセットは placeholder で実装し、出典 URL を同ファイルに残す。
3. `/home` の UI 実装は最小差分で追加し、既存機能（バックテスト導線）を壊さない。

---

保存先:
- docs/PLAN/assets/home_en_full.png
- docs/PLAN/assets/home_en_resources.json
- docs/PLAN/assets/home_en_resources_perf.json

（注）画像等の原本をリポジトリに入れる前に必ず権利確認を行ってください。
