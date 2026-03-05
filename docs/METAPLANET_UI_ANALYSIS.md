# Metaplanet UI 解析レポート

## 概要
このレポートは https://analytics.metaplanet.jp/?lang=ja の公開HTMLと関連スタイルシートを取得して解析した結果をまとめたものです。サーバ側で配信されるHTMLはReact等のSPAバンドルで、動的にチャートやダッシュボード要素を描画します。ここでは取得可能な静的資産（HTML、CSS、ロゴ画像URL等）から「参照用UI諸元」「カラーパレット」「フォント」「主要コンポーネント分割案」を抽出しています。なお、この実行環境から実ページのレンダリング（ピクセルスクリーンショット）の生成は行っていません。スクリーンショットを取得する手順は後述します。

## 取得済みファイル
- ページHTML: https://analytics.metaplanet.jp/?lang=ja（取得済み）
- メインCSS: https://strategytracker.com/static/dist/assets/index-C41_S0LL.css（取得済みの断片あり）
- メインJS(バンドル): https://strategytracker.com/static/dist/assets/index-BtD56X-I.js（HTMLにscriptで指定）
- Font Awesome: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css（取得済み）
- ロゴ画像（公開URL）:
  - https://strategytracker.com/static/images/dashboardLogos/metaplanetLogo.png
  - https://strategytracker.com/static/images/dashboardLogos/metaplanetMobileLogo.png

## ページタイプ
- SPA（クライアントサイドでJSバンドルが描画）
- React等で #root にマウントされる構成（HTMLに <div id="root"></div> が存在）

## 主なUI要素（HTML/CSSから抽出）
- ヘッダー / ロゴ（パートナーロゴを表示、homeLink が指定）
- company-dropdown / company-toggle（企業選択用カスタムドロップダウン）
- hero セクション（タイトル・リード・CTA）
- features-grid（グリッド表示の機能カード）
- premium CTA（購読促進セクション、ボタン・説明）
- notification / popup banners（通知バナー、成功・警告・エラーのスタイルあり）
- discussion / recent discussions（議論・スレッドのプレビュー群）
- metric-card / dashboard panels（チャートやメトリックカードを組む部分）
- leaflet（地図/タイル）に関するCSS定義が含まれている（地図系コンポーネント使用の可能性）

## 主要スタイル要素（抽出）
- フォント: body に Segoe UI, Tahoma, Geneva, Verdana, sans-serif が指定されています。
- コンテナ: .page-container { max-width: 1200px; margin: 0 auto; padding: 20px 15px }
- ブレークポイント: 992px, 768px, 576px 等のレスポンシブ調整あり
- シャドウ / ボーダー: 一貫して細かい box-shadow と border-radius を使用

### カラーパレット（CSS断片から）
- --primary-color-rgb: 0, 123, 255  → primary color: rgb(0,123,255) / #007BFF
- アクセントやボタン等に #3b82f6, #e6f7ff などの青系バリエーション
- 成功: #d1e7dd / #a3cfbb（success-color近辺）
- 警告: #fff3cd / #ffe69c
- エラー: #f8d7da / #f5c2c7
- テキスト色: #333（ダーク） / #555（ミディアム） / #666（補助）

※ 上記は取得したCSSの断片から抽出した主要色／変数の一覧です。:root や変数定義はCSSの先頭付近にまとまっている可能性があるため、完全な色変数一覧が必要ならCSS全体の追加取得を行います。

## レイアウトとコンポーネント候補（提案）
下記コンポーネント分割は、既存SPAを参考に再実装またはUIを模倣する際の出発点です。

- Header
  - props: partnerName, partnerLogoUrl, homeLink, isLoggedIn
- CompanyDropdown
  - props: companies[], selectedCompany, onSelect
- Hero
  - props: title, leadText, primaryCTA (label, onClick)
- FeatureCard (再利用可能)
  - props: icon, title, description, links[]
- MetricCard / ChartPanel
  - props: metricData, chartType, title, subtitle
- PopupBanner / Notification
  - props: type (info/success/warning/error), title, message, dismiss
- DiscussionList / DiscussionCard
  - props: items[], onOpen
- Footer
  - props: links[]

各コンポーネントはTailwindやCSS Modules/SCSSで分離可能ですが、既存CSSを活用する場合はクラス名を再利用する方が速いです。

## スクリーンショット取得（ローカルでの手順）
この環境ではブラウザレンダリングとフルページスクリーンショット生成ができないため、ローカルでの実行手順を示します（Windows PowerShell例）。

1. Node.js をインストール（未導入の場合）
2. ワークディレクトリで: npm init -y
3. Puppeteer をインストール: npm install puppeteer --save-dev
4. 以下を screenshot.js として保存:

```js
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({args:['--no-sandbox','--disable-setuid-sandbox']});
  const page = await browser.newPage();
  await page.goto('https://analytics.metaplanet.jp/?lang=ja', {waitUntil: 'networkidle2'});
  await page.setViewport({width: 1366, height: 768});
  await page.screenshot({path: 'metaplanet_full.png', fullPage: true});
  await browser.close();
})();
```

5. PowerShell で: node screenshot.js → metaplanet_full.png が生成されます。

（CIで自動取得したい場合はPlaywrightやヘッドレスChromiumを利用するスクリプトをCIに組み込むことを推奨します）

## 次のアクション（選べます）
- A: この解析レポートをさらに詳細化して、CSS変数すべて・クラス一覧・DOMツリーマップを作成する
- B: ローカルで実行するための Puppeteer スクリプトをこのリポジトリ内に追加（例: scripts/screenshot-metaplanet.js）してPRを作成する
- C: このレイアウトを元に React コンポーネントの雛形（TSX）を生成する

希望する次のアクションを教えてください（例: A / B / C）。

---

解析日時: 2026-03-05T07:27:35.338Z
元URL: https://analytics.metaplanet.jp/?lang=ja

（注）取得した画像は外部URLを参照しているため、実際の画像ファイルはリポジトリに保存していません。必要なら画像をダウンロードして添付します。