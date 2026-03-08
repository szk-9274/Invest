# product-specs

目的: 機能仕様書の保管

テンプレート:
- 機能名
- 目的
- 前提条件
- 期待動作
- UI ワイヤーフレーム / 操作フロー
- テスト条件

例:
- Backtest Dashboard — TradingView 風チャート表示
  - 期待動作: PNG を背景に OHLC を重ねて表示、エントリ/イグジットはマーカーで示す
  - テスト条件: /api/backtest/latest と /api/backtest/ohlc の契約テストが通ること
