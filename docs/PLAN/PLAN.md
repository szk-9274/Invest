# 実装計画: トップ5/ボトム5 購入チャート (ECharts)

## 概要
analytics.metaplanet.jp の購入チャートを参考に、散布図で各購入を点で表示し、点にホバーすると日時と購入額がツールチップで表示され、点の大きさで購入額が一目で分かるUIを実装する。TOPページに「TOP5」と「BOTTOM5」の合計10個のチャートをグリッドで並べて表示することをゴールとする。

## 主要方針
- 可視化ライブラリ: ECharts を採用（scatter 系、symbolSize と tooltip の柔軟性が高い）。
- データ形式（API → フロント）
  - 各資産は次のような構造を持つ:
    {
      "assetId": "btc",
      "assetName": "Bitcoin",
      "purchases": [
        { "timestamp": 1672531200000, "price": 50000, "amount": 120000 },
        ...
      ]
    }
  - API は top5 と bottom5 をそれぞれ配列で返却する（例: { top: [...], bottom: [...] }）。
- 見た目のルール: 点の面積 ∝ 購入額 の関係を満たすため、symbolSize は半径 ∝ sqrt(amount) * scaleFactor として調整する。

## 実装ステップ（高レベル）
1. データ定義
   - バックエンドとフロントで共通のデータフォーマットを決定（timestamp は ms、price/amount は数値）。
   - 1チャートあたりの最大点数を定義（例: 100点）やサンプリング方針を決める。
2. バックエンド
   - GET /api/charts/top-bottom?limit=5 のようなエンドポイントを設計・実装する。
   - top/bottom の判定ロジックと、各 asset ごとに purchases 配列を返却する処理を作る。
   - 大量データ時は事前集計やサンプリングを行う。
3. フロントエンド
   - 再利用可能な Chart コンポーネント（ECharts）を作成する。
     - series.type = 'scatter'
     - data = [ [timestamp(ms), price, amount], ... ] の形式を受け取る。
     - symbolSize: val => Math.sqrt(val[2]) * SCALE: でサイズを制御。
     - tooltip: 日時をローカル表記、購入額はカンマ区切りで表示するフォーマッタを実装。
   - ページコンポーネントで API からデータ取得し、TOP5/BOTTOM5 をそれぞれ Chart に渡す。
4. レイアウト
   - 10個のチャートを読みやすいグリッドで表示（レスポンシブ対応）。
   - チャートタイトルに assetName と合計購入額のサマリを表示。
5. スタイリング・アクセシビリティ
   - 色とコントラスト、フォーカス時の視認性、キーボード操作でのポイント選択（可能な範囲）を確認。
6. テスト
   - Chart コンポーネントのユニットテスト（tooltip フォーマット、symbolSize の計算）
   - エンドツーエンドや統合テストでページ表示検証。

## TODO（チケット一覧）
- define-data-shape: バックエンド/フロントで使うデータ形式を定義する（JSON例、最大点数、タイムゾーン方針）。
- backend-api-top-bottom: GET /api/charts/top-bottom?limit=5 を実装する（必要な集計を行い返却）。
- frontend-echarts-component: ECharts を使った再利用可能な散布図コンポーネントを作成する（tooltip、symbolSize 実装）。
- frontend-top-bottom-page: Top/Bottom ページを作成して 10 個のチャートをグリッド表示するページを作成。APIからデータ取得を行う。
- styling-and-accessibility: カラーパレット、フォーカス/キーボード動作、レスポンシブ対応の実装。
- tests-and-validation: 単体・統合テストの追加と表示検証。

## 注意点・リスク
- 点数が多い場合はレンダリング性能に注意。サンプリングや事前集計を検討する。 
- symbolSize の scaleFactor は実データで調整が必要。
- フロントのフレームワーク（React/Vue）によってコンポーネント実装の細部が変わるので、まず package.json を確認する。

## 成果物
- このファイル (plan.md)
- session DB の todos に上記タスクを登録済み

----
(注) 実装を開始する前に、フロントのフレームワーク確認と API の仕様確定を推奨する.
