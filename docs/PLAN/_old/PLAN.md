# 実装計画: TOP5/BOTTOM5 購入チャート — analytics.metaplanet.jp 参考

## 2026-03-05 レビュー結果（確定）

- 本リポジトリの frontend は React 18 + Vite。ターゲットサイト側の React バージョン推定は実装根拠にしない。
- 第1タスク（/dashboard）は **/dashboard のみ** に適用し、既存 API（`/api/backtest/latest`, `/api/backtest/results/{timestamp}`）の `trades` と `ticker_stats` を再利用して Plotly 散布図を実装する（新規 API 追加は後続候補）。
- 第2タスク（/home）は `docs/PLAN/home-assets.md` の分類結果を参照し、ライセンス確認済みアセットのみ使用する。
- 第3タスク（サイト全体日本語化）は `docs/PLAN/plan-sitewide-i18n.md` を正とし、右上トグル（EN/JA）を全ページ共通ヘッダーに実装する。

## Task1 STEP 1: PLAN（/dashboard Plotly 実装）

### 変更箇所（予定）

- frontend/src/pages/BacktestDashboard.tsx
  - Charts タブの表示を Plotly ベースの TOP5/BOTTOM5 購入散布図グリッドに差し替え（/dashboard 限定）。
- frontend/src/components/（新規）
  - Plotly 散布図コンポーネント（例: `TopBottomPurchaseCharts.tsx`）を追加。
- frontend/src/components/*.test.tsx（新規）
  - symbol size 計算、hover 文言、空データ表示のテストを追加。
- docs/COMMAND.md
  - /dashboard の確認コマンドとテストコマンドを追記。

### 影響範囲

- 影響あり: /dashboard の Charts タブ表示。
- 影響なし: /home, /chart/:ticker, backend の既存 API 契約。

### 受け入れ基準

- /dashboard の Charts タブで Top5/Bottom5 の最大10チャートが表示される。
- 点サイズが `sqrt(amount)` でスケーリングされる。
- ホバーで日時・価格・購入額が表示される。
- データ未取得時はクラッシュせず空状態メッセージを表示する。

### 参照アセット・参照 URL

- https://analytics.metaplanet.jp/?lang=ja&tab=charts（UI 参照）
- 外部画像はこのタスクでは新規追加しない。

### STEP 3: REVIEW（Task1 実装後）

- 機能: `/dashboard` の Charts タブで Plotly ベースの TOP/BOTTOM 購入散布図を表示する実装に差し替え、空データ時はメッセージ表示を確認。
- アクセシビリティ: テキストラベル（TOP/BOTTOM バッジ）と既存タブ操作を維持し、キーボードフォーカス挙動は既存実装を維持。
- パフォーマンス: Plotly コンポーネントを `React.lazy` で遅延ロードし、初期バンドルを分離（チャートタブ表示時のみ読み込み）。
- ライセンス: Task1 では外部画像・フォントを新規導入していないため、追加ライセンス確認項目はなし。
- 検証コマンド:
  - `npm --prefix frontend run test`
  - `npm --prefix frontend run build`

## 目的

- analytics.metaplanet.jp の Charts UI に近づけ、TOP5/BOTTOM5 の購入チャートを合計10個グリッドで表示する。

## 現状観察（ターゲットサイト）

- 技術スタック: ESM モジュール（script type="module"、modulepreload）、ビルド成果物は /static/dist/assets 配下（Vite/Rollup 系の出力に近い）。
- ライブラリ痕跡: Leaflet の CSS クラス（leaflet-*）が確認され、地図表示を利用している箇所がある。外部スクリプトとして Google Analytics、Rewardful、embed.metaplanet.jp 等を使用。
- チャートライブラリ: main bundle に含まれる可能性が高く、明確な文字列（plotly/echarts/highcharts）が HEAD に見えないため一部は動的チャンクで読み込まれている可能性がある（要追検）。
- UI 備考: 散布図で購入を点表示、ホバーで日時と購入額を表示、点の大きさで購入額を視覚化、レスポンシブなグリッド配置。

## 推奨方針（要点）

- 短期での再現性を優先し、既存リポジトリにある Plotly（react-plotly.js）をまず活用することを推奨。既存依存を活かせるため実装コストが低く、必要時に ECharts へ切替える選択肢を残す。
- React/Vite の構成は類似しているため、フロント側は現状の構成を維持しつつ Chart コンポーネントを追加する。将来的な React 19 へのアップグレードは別タスクで対応。

## API 契約（詳細）

- エンドポイント（後続候補）: GET /api/charts/top-bottom?limit=5&maxPointsPerAsset=100
- パラメータ:
  - limit: number (default 5)
  - maxPointsPerAsset: number (バックエンドが返す各 asset あたりの最大点数)
- レスポンス例:
{
  "top": [
    {
      "assetId": "btc",
      "assetName": "Bitcoin",
      "totalAmount": 123456.78,
      "purchases": [
        { "timestamp": 1672531200000, "price": 50000.0, "amount": 120000.0 },
        ...
      ]
    }, ...
  ],
  "bottom": [ ... ]
}
- 仕様:
  - timestamp は ms (UTC)。price/amount は数値。
  - 大量データ対策としてバックエンドは maxPointsPerAsset を尊重し、事前サンプリングまたはダウンサンプリング（タイムバケット、上位N件、ランダム/リザーバー）を行う。

## フロント実装（コンポーネント設計）

- ChartScatter コンポーネント（再利用可能）
  - Props:
    - data: Array<[timestamp(ms), price, amount]> または asset オブジェクト
    - title: string
    - width?: number, height?: number
    - scale?: number (symbolSize の係数)
    - useWebGL?: boolean (大量点時は Plotly の scattergl を利用)
    - onPointClick?(pointData)
  - 動作:
    - symbolSize = Math.sqrt(amount) * scale
    - tooltip は日時をローカル表記、price/amount は千区切りで表示
    - WebGL/canvas 切替で大量点を扱う
- TopBottomGrid ページ
  - API から top/bottom を取得し、2x5 またはレスポンシブで 10 チャートをグリッド表示
  - IntersectionObserver による遅延ロード（画面外はレンダリング遅延）

## バックエンド実装（要点）

- GET /api/charts/top-bottom を実装（既存の screening/backtest 出力を再利用できるか確認）
- サンプリング方針を実装: maxPointsPerAsset に応じて downsample（例: 時系列均等サンプリング、あるいは金額上位 N 件）
- 大量データ時のパフォーマンス対策: キャッシュ / 事前集計 / ペイロード圧縮

## パフォーマンス / 可観測性

- フロント: チャートは必要時に dynamic import、IntersectionObserver で遅延ロード、WebGL を使うことで大量点を描画
- バック: キャッシュ、gzip 圧縮、API レイテンシ計測を導入

## テスト

- フロント: vitest + @testing-library/react による Chart コンポーネントのユニットテスト（tooltip 表示、symbolSize 計算）
- バック: FastAPI の TestClient（または既存のテストフレームワーク）で API 契約テスト・サンプリング検証（モックデータ使用）
- E2E: 必要に応じて Playwright でページ表示と主要インタラクションを確認

## タスク一覧 (要チケット化)
- plan-define-data-shape: データフォーマットを確定する（timestamp ms/UTC、price/amount の単位、maxPointsPerAsset、タイムゾーン方針）
- plan-chartlib-decision: チャートライブラリ選定（Plotly を推奨。ECharts を採用する場合は差分を定義）
- backend-api-top-bottom: /api/charts/top-bottom の実装（サンプリング含む）
- frontend-chart-component: ChartScatter コンポーネントの実装（Plotly scatter/scattergl を想定）
- frontend-top-bottom-page: Top/Bottom ページの実装（10 チャートのグリッド）
- performance-sampling: サンプリング・WebGL 切替・遅延ロードの実装と検証
- tests-and-validation: 単体・統合・E2E テストの追加
- docs-update: README/COMMAND.md に起動手順と検証コマンドを追記
- accessibility: カラーパレット、キーボード操作、フォーカス管理の検証と修正

## 受け入れ基準
- API から取得した top/bottom データで 10 個のチャートが表示される
- 各点にホバーで日時・購入額が表示され、点の大きさが購入額を反映する
- デスクトップ・モバイル両方でレイアウトが崩れない
- 大量データでもレンダリングが著しく固まらない（初回描画 1s 未満を目標）

## 次のアクション（短期）
1. Task1 は frontend のみで実装し、既存 backtest API レスポンスを利用して /dashboard の Plotly チャートを完成させる。
2. backend の `/api/charts/top-bottom` は Task1 完了後に必要性を再評価して別タスク化する。

---

変更内容を確認してレビューをお願いします。

## 適用範囲

- 本計画での TOP5/BOTTOM5 チャート実装は http://localhost:3000/dashboard のみ適用する。
- /home ページの実装は別途追加の計画とタスクを用意して進める（下記）。

## /home (http://localhost:3000/home) — metaplanet.jp/en 参考

### 目的

- Metaplanet の英語ページ (https://metaplanet.jp/en) に近いマーケティング／ランディングページを当リポジトリの frontend 上で再現し、ブランド紹介、購読 CTA、機能説明を行うトップページを作る。

### 取得した情報（フェッチ結果）

- GET https://metaplanet.jp/en のサーバー応答は簡潔なテキスト（著作権表記など）で、フルレンダリング済みの HTML は返らないか、クライアント側で JS によって構築されるページである可能性がある（server-side で最小限の HTML が返り、完全な UI はクライアント実行時に生成される想定）。
- HTML レンダリングからは明確なフレームワークやビルド手法を判定できなかったため、内部実装に依存せず現行の React + Vite 構成で再現するのが現実的。

### 再現すべき見た目・挙動（優先度高→低）

1. ヒーローセクション: 大きな見出し・サブテキスト、背景画像またはテクスチャ、中央に購読CTAボタン
2. 機能/特徴ブロック: アイコン＋短文のカードをグリッドで配置
3. ロゴ群（掲載実績）: パートナー／掲載ロゴの横並び
4. シンプルで読みやすいヘッダー（言語切替を含む）とフッター（会社情報・著作権）
5. レスポンシブ対応（モバイル・タブレットでのレイアウト崩れ防止）
6. アナリティクス等の埋め込みスクリプト（既存 backend/frontend の設定と整合）

### 技術方針（推奨）

- 既存 frontend (React + Vite) に HomePage コンポーネントを追加して実装。
- スタイリングは既存の tailwind.config.js を利用するか、既存 CSS に合わせる（Tailwind を使う選択は既存設定次第）。
- 画像系アセットはリポジトリに追加して最初は静的に配置。将来的に CMS 連携が必要なら後続で検討。
- 多言語は最小限の i18n 基盤（例: react-i18next の導入）を設け、英語ページ (/home) を先行で作成する。

### 実装ステップ（高レベル）

1. plan-home-collect-assets: metaplanet.jp/en の重要セクションをスクリーンショットで保存し、必要なテキスト・画像を列挙する。デザインの雛形を決定する。  
2. plan-home-routing: frontend に /home ルートを追加し、共通レイアウト（Header/Footer）を適用する。  
3. plan-home-implementation: HomePage コンポーネント実装（Hero → Features → Logos → CTA → Footer）。  
4. plan-home-seo-accessibility: Meta / OG タグ・構造化データ・キーボードアクセス・コントラスト確認を行う。  
5. plan-home-tests: vitest（ユニット）と Playwright（スモークE2E）で主要表示とレスポンシブを確認。  
6. plan-home-docs: README/COMMAND.md にローカルでの表示確認手順を追記。

### 受け入れ基準（Home）

- /home を開くとヒーロー・CTA・特徴カード・ロゴ群が表示され、主要なビューポートでレイアウトが崩れないこと。  
- メタ情報（title, description, og:image 等）が設定されていること。  
- 基本的なアクセシビリティ（キーボード操作、色コントラスト）が担保されていること。

### タスク（todos 提案）
- plan-home-collect-assets: metaplanet.jp/en のスクショとアセット一覧作成（pending）
- plan-home-routing: /home ルーティング追加（pending）
- plan-home-implementation: HomePage コンポーネント実装（pending）
- plan-home-seo-accessibility: SEO・アクセシビリティ対応（pending）
- plan-home-tests: テスト追加（pending）
- plan-home-docs: ドキュメント更新（pending）

## 参考にした外部 URL（取得・確認済み）

- https://analytics.metaplanet.jp/?lang=ja&tab=charts
- https://strategytracker.com/
- https://strategytracker.com/static/dist/assets/index-BtD56X-I.js
- https://strategytracker.com/static/dist/assets/index-C41_S0LL.css
- https://strategytracker.com/static/dist/assets/trackerLogo-IzRY_TcI.png
- https://strategytracker.com/static/dist/assets/satoshiLogo-HMx3UzIr.png
- https://strategytracker.com/static/dist/assets/trackerDeepGroundLogo-CEm9BUFc.png
- https://strategytracker.com/static/images/dashboardLogos/metaplanetLogo.png
- https://strategytracker.com/static/images/trackerGroundLogo.png
- https://embed.metaplanet.jp/footer.js
- https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
- https://r.wdfl.co/rw.js
- https://www.googletagmanager.com/gtag/js?id=G-LTQ5T9F6CP
- https://metaplanet.jp/en
- https://metaplanet.jp/

（上記は本作業で取得・確認した主要な外部リソースです。静的列挙に加えて headless キャプチャ実行済みで、詳細は `docs/PLAN/home-assets.md` と `docs/PLAN/assets/` を参照。）

### 実行概要
- 実施内容: 公開 HTML（https://metaplanet.jp/en, https://metaplanet.jp）を取得し、HTML 内の preload/link/script/img 等から静的リソース URL を抽出。
- 実行手段: web_fetch による静的取得。クライアント実行時に動的に読み込まれるチャンクや遅延ロードは取得できないため、完全なスクリーンショットは未取得。
- 実行ログ: docs/PLAN/home-assets.md に手順・推奨スクリプトを保存済み。

### 取得した主要アセット（抜粋）

- ロゴ（preload）:
  - https://metaplanet.jp/images/logos/light/_012.svg
  - https://metaplanet.jp/images/logos/dark/_012.svg
  - https://metaplanet.jp/images/logos/light/_015.svg
  - https://metaplanet.jp/images/logos/dark/_015.svg

- Hero / 背景画像:
  - https://metaplanet.jp//images/planets-hero.jpeg
  - https://aqsmixvnbavrufgttwsn.supabase.co/storage/v1/object/public/images/home-page.jpg

- CDN ロゴ:
  - https://aqsmixvnbavrufgttwsn.supabase.co/storage/v1/object/public/images/logos/METAPLANET-M-Only-wCircle_ORANGE.png

- CSS（Next.js 出力）:
  - /_next/static/css/cf2af83f588f3be0.css?dpl=...
  - /_next/static/css/a8d12fb7c765706d.css?dpl=...
  - /_next/static/css/fd9ae5657ac7550b.css?dpl=...

- JS チャンク（多数、遅延ロード）:
  - /_next/static/chunks/*.js
  - /_next/static/chunks/app/%5Blocale%5D/page-*.js

- Favicons / manifest:
  - /favicons/manifest.json
  - /favicons/favicon.ico
  - /favicons/icon.svg
  - /favicons/icon-192.png
  - /favicons/icon-512.png
  - /favicons/apple-icon.png
  - /favicons/mask-icon.svg

- 追加情報ソース:
  - application/ld+json にロゴ・hero 画像 URL と組織情報が含まれる（上記 Supabase の画像 URL 等）

### 注意点 / 次のステップ
- この静的列挙は HTML に明記されたリソースの一覧を取得したに過ぎず、画面描画直後やインタラクションで追加読み込みされるリソース（遅延ロード画像、動的チャンク）は headless ブラウザでのキャプチャが必要。
- headless キャプチャ（推奨: Playwright）を行う場合のコマンド例:
  - npx playwright install
  - npx playwright screenshot https://metaplanet.jp/en --output=docs/PLAN/assets/home_en_full.png --full-page
  - 付属スクリプト: node scripts/capture-home-assets.js（docs/PLAN/home-assets.md に例あり）

---

（続けて headless キャプチャを実行する／こちらで実行する、どちらを希望しますか？）

### Headless キャプチャ実行結果
- キャプチャをこの環境で実行しました。出力ファイル: docs/PLAN/assets/home_en_full.png, docs/PLAN/assets/home_en_resources.json, docs/PLAN/assets/home_en_resources_perf.json
- スクリーンショットと resource JSON は docs/PLAN/assets に保存済み。docs/PLAN/home-assets.md に生成日時とサイズを追記しました。

### /home アセット分類（ヘッドレスキャプチャ結果）
- 生成物: docs/PLAN/assets/home_en_full.png, docs/PLAN/assets/home_en_resources.json, docs/PLAN/assets/home_en_resources_perf.json
- 概要: 取得したリソースを大分類し、実装に必要なアセット（Hero, Logo, Partner logos, Icons, Fonts）を特定しました。フォントと一部画像はライセンス確認が必要です。

#### 抜粋分類（代表例）
- ヒーロー画像: https://metaplanet.jp//images/planets-hero.jpeg
- ロゴ: https://metaplanet.jp/images/logos/light/_012.svg, https://metaplanet.jp/images/logos/dark/_012.svg, https://metaplanet.jp/images/logos/light/_015.svg
- パートナーロゴ: https://metaplanet.jp/images/partners/bitcoin.jp-white.svg, https://metaplanet.jp/images/partners/bm-japan-white.svg
- アイコン: https://metaplanet.jp/images/companies/linkedin-icon.svg, https://metaplanet.jp/images/companies/youtube-icon.svg
- フォント（要確認）: /_next/static/media/*.woff2
- CSS / JS（実装参照）: /_next/static/css/*.css, /_next/static/chunks/*.js

#### 次の推奨作業
1. Hero と Header ロゴを最優先で承認・ダウンロード（低解像度で一旦保存して実装検証）。
2. フォントはライセンス確認後に置換／導入を決定。フォント不可の場合は Web 安全フォントで代替。
3. パートナー/掲載ロゴの利用許諾を確認。許諾取れない場合はプレースホルダ化。
4. 取得リストとライセンス情報を docs/PLAN/assets-licenses.md にまとめる。

（詳細は docs/PLAN/home-assets.md を参照）
