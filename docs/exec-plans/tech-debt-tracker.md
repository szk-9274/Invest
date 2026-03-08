# tech-debt-tracker

目的: 技術的負債の一覧と優先度管理

フォーマット:
- id: short-id
- 説明: 簡潔な説明
- 影響範囲: どのモジュールに影響するか
- 優先度: high/medium/low
- 回避案: 短期的対応策

例:
- td-001
  - 説明: Puppeteer の headless 実行が不安定
  - 影響範囲: CI のスクリーンショット取得
  - 優先度: high
  - 回避案: 手動キャプチャ or 設定調整 (--no-sandbox 等)
