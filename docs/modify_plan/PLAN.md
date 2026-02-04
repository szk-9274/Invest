# 📌 Claude Code 指示書（Phase 2 実装）

## 🎯 目的（Phase 2）

Phase 1 で実装済みの **TradingView 風チャート生成機能**を拡張し、  
**実際のトレード履歴（trade_log）と連携して IN / OUT を可視化**する。

---

## 1️⃣ 現状整理（前提）

- Phase 1 では以下が実装済み：
  - 年間ローソク足チャート
  - SMA 20 / 50 / 200
  - Bollinger Bands
  - Volume
  - ダークテーマ（TradingView 風）
- **IN / OUT マーカーは未実装**
- trade_log.csv は既に存在し、以下を含む：
  - ticker
  - entry_date / exit_date
  - entry_price / exit_price
  - side (LONG / SHORT)
  - pnl

---

## 2️⃣ Phase 2 で実装する内容

### A. チャートへの IN / OUT マーカー描画

#### 要件
- 対象：`trade_log.csv`
- 各ティッカーについて：
  - ENTRY → ▲（緑）
  - EXIT → ▼（赤）
- 複数トレードが **同一チャート上に全て描画されること**
- 年間チャート（Phase 1 と同一 UI）

#### 実装方針
- `generate_price_chart()` を拡張 or ラッパー関数を追加
- trade_log をティッカー単位でフィルタ
- matplotlib / mplfinance の `make_addplot` を使用

---

### B. デフォルトモードの自動チャート生成

#### 挙動（重要）

バックテスト完了後に以下を自動実行：

1. `ticker_stats.csv` から  
   - **P&L 上位5銘柄**
   - **P&L 下位5銘柄**
   を抽出

2. 各銘柄について：
   - 年間チャートを生成
   - IN / OUT マーカーをすべて描画
   - 以下に保存：

output/charts/
├── top_01_AAPL.png
├── top_02_NVDA.png
├── ...
├── bottom_01_TSLA.png
└── bottom_02_META.png

yaml
コードをコピーする

---

### C. CLI / 実行モードの設計

#### 新しいデフォルト挙動

python main.py backtest

diff
コードをコピーする

⬇ 自動で以下を実行：

- バックテスト
- trade_log.csv 出力
- ticker_stats.csv 出力
- 上位5 / 下位5 銘柄のチャート生成（IN/OUT付き）

#### オプション指定（任意）

python main.py chart --ticker AAPL

yaml
コードをコピーする

- 単一ティッカーのチャート生成
- trade_log が存在すれば IN / OUT を描画

---

## 3️⃣ README.md への追記（必須）

### 追記内容（そのまま使える）

```md
## Chart Generation (TradingView-like)

### Generate charts after backtest (default)
```bash
python main.py backtest
This will:

Run backtest

Generate trade_log.csv and ticker_stats.csv

Automatically generate charts for:

Top 5 profitable tickers

Bottom 5 least profitable tickers

Charts include:

Candlesticks

SMA 20 / 50 / 200

Bollinger Bands

Volume

IN / OUT trade markers

Generate chart for a specific ticker
bash
コードをコピーする
python main.py chart --ticker AAPL
Output:

bash
コードをコピーする
output/charts/AAPL.png
yaml
コードをコピーする

---

## 4️⃣ テスト方針（TDD 継続）

### 追加テスト

- trade_log がある場合：
  - ENTRY / EXIT マーカーが描画される
- trade_log がない場合：
  - マーカーなしでもエラーにならない
- 上位 / 下位銘柄が正しく選ばれる
- 出力ファイル名が期待通り

---

## 5️⃣ Phase 2 完了条件（Definition of Done）

- [ ] IN / OUT がチャート上に可視化される
- [ ] 上位5 / 下位5 銘柄のチャートが自動生成される
- [ ] README にコマンド使用方法が明記されている
- [ ] 既存テストが壊れない
- [ ] coverage 80%以上維持