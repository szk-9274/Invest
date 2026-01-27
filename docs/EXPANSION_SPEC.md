# 株式スクリーニングシステムの機能拡張

## 現在の状況
- GitHubリポジトリ: https://github.com/szk-9274/Invest
- 実装済み: Stage 2判定（S&P 500の98銘柄で動作確認済み）
- 出力: `output/screening_results.csv`

---

## 拡張タスク

### タスク1: スクリーニング対象の大幅拡張

**目的**
98銘柄から約3,500銘柄に拡張し、より多くのStage 2候補を発見する。

**対象銘柄**
| カテゴリ | 銘柄数 | 特徴 |
|---------|--------|------|
| S&P 500 | 約500 | 米国大型株 |
| NASDAQ Composite | 約3,000+ | ハイテク中心 |
| Russell 3000 | 約3,000 | 米国市場98%カバー |
| 中型株以上 | 約2,500-3,500 | 時価総額20億ドル以上 |

**実装要件**
1. `scripts/update_tickers.py`を拡張
2. yfinanceで以下を取得:
   - S&P 500: Wikipedia経由
   - NASDAQ: yfinanceの`.tickers`リスト
   - Russell 3000: 公開リスト取得
3. 重複除外・時価総額フィルター（20億ドル以上）
4. 最終的に約3,500銘柄を`config/tickers.csv`に保存

**yfinanceで取得可能な方法**
```python
# 例: NASDAQ全銘柄
import yfinance as yf
import pandas as pd

# NASDAQスクリーナーを使用
nasdaq_tickers = pd.read_html('https://www.nasdaq.com/market-activity/stocks/screener')[0]

# Russell 3000はCSV等から取得
# https://www.ishares.com/us/products/239714/ishares-russell-3000-etf
```

---

### タスク2: ファンダメンタルズフィルターの追加

**目的**
ミネルヴィニ戦略の「成長株」条件を追加。テクニカル+ファンダで絞り込み。

**追加条件**
1. **EPS成長率**: 前年同期比 +25%以上（理想は+50%以上）
2. **売上高成長率**: 前年同期比 +25%以上
3. **四半期加速**: QoQ（四半期対前期）でも成長
4. **利益率**: 営業利益率 15%以上（オプション）

**yfinanceでの取得方法**
```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
info = ticker.info

# 取得可能なファンダメンタルズ
eps_growth = info.get('earningsQuarterlyGrowth', 0)  # EPS成長率
revenue_growth = info.get('revenueGrowth', 0)        # 売上成長率
operating_margin = info.get('operatingMargins', 0)   # 営業利益率

# 四半期データ
earnings = ticker.quarterly_earnings
financials = ticker.quarterly_financials
```

**実装場所**
- 新規ファイル: `python/analysis/fundamentals.py`
- クラス: `FundamentalsAnalyzer`
- `screener.py`に統合

**フィルター条件**
```python
@dataclass
class FundamentalsFilter:
    min_eps_growth: float = 0.25      # 25%以上
    min_revenue_growth: float = 0.25  # 25%以上
    min_operating_margin: float = 0.15  # 15%以上（オプション）
    require_qoq_acceleration: bool = True  # 四半期加速必須
```

**config/params.yamlへの追加**
```yaml
# ファンダメンタルズフィルター
fundamentals:
  enabled: true
  min_eps_growth: 0.25        # 25%
  min_revenue_growth: 0.25    # 25%
  min_operating_margin: 0.15  # 15%
  require_qoq_acceleration: true
```

---

### タスク3: バックテストエンジンの実装

**目的**
過去5年（2020-2025）のStage 2銘柄でエントリーした場合のパフォーマンスを検証。

**実装要件**

#### 3-1. バックテストエンジン
ファイル: `python/backtest/engine.py`

**機能**
1. 過去データで日次スクリーニング
2. Stage 2 + VCP条件でエントリー
3. 50日MA割れでエグジット
4. ポートフォリオ管理（最大5銘柄同時保有）
5. パフォーマンス計測

**出力指標**
- 年率リターン（CAGR）
- 最大ドローダウン（Max DD）
- シャープレシオ
- 勝率
- 平均利益 vs 平均損失
- 総トレード数

**実装例**
```python
class BacktestEngine:
    def __init__(self, config: Dict):
        self.initial_capital = config['backtest']['initial_capital']
        self.max_positions = config['backtest']['max_positions']
        self.commission = config['backtest']['commission']
    
    def run(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        バックテスト実行
        
        Returns:
            {
                'cagr': 0.15,           # 年率15%
                'max_drawdown': 0.12,   # 最大12%下落
                'sharpe_ratio': 1.8,
                'win_rate': 0.62,       # 勝率62%
                'avg_gain': 0.25,       # 平均+25%
                'avg_loss': 0.07,       # 平均-7%
                'total_trades': 87,
                'equity_curve': pd.Series  # 資産曲線
            }
        """
        pass
```

#### 3-2. 実行コマンド
```powershell
# バックテスト実行
python main.py --mode backtest --start 2020-01-01 --end 2025-01-27

# 特定銘柄のみ
python main.py --mode backtest --tickers AAPL MSFT GOOGL
```

#### 3-3. 結果の可視化
- 資産曲線グラフ（matplotlib）
- 月次リターン表
- トレード詳細CSV出力

**出力例**
```
================================================================================
BACKTEST RESULTS (2020-01-01 to 2025-01-27)
================================================================================
Initial Capital:      $10,000
Final Capital:        $21,345
Total Return:         +113.45%
CAGR:                 16.3%
Max Drawdown:         -18.2%
Sharpe Ratio:         1.92
Win Rate:             64.5%
Avg Gain:             +28.3%
Avg Loss:             -6.8%
Total Trades:         142
Best Trade:           NVDA +156%
Worst Trade:          ZM -9.2%
================================================================================
```

---

## 実装の優先順位

### Phase 1（最優先）
1. タスク1: 銘柄リスト拡張（3,500銘柄）
2. タスク2: ファンダメンタルズフィルター追加

### Phase 2
3. タスク3: バックテストエンジン実装

---

## 技術的な制約・注意点

### yfinanceの制限
1. **レート制限**: 1秒あたり2リクエスト程度
   - 3,500銘柄 × 0.5秒 = 約30分
   - 並列処理で10-15分に短縮可能

2. **データ欠損**: 上場廃止・ティッカー変更
   - 自動的にスキップ（既に実装済み）

3. **ファンダメンタルズデータ**: 全銘柄で取得可能だが遅い
   - キャッシュ機能の実装推奨

### パフォーマンス最適化
```python
# 並列処理（オプション）
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_ticker, tickers))
```

---

## 設定ファイルの変更

### config/params.yaml に追加
```yaml
# データソース（拡張）
data:
  source: "yfinance"
  target_categories:
    - "sp500"           # S&P 500
    - "nasdaq"          # NASDAQ Composite
    - "russell3000"     # Russell 3000
  min_market_cap: 2_000_000_000  # 20億ドル
  min_price: 5.0
  min_volume: 500_000
  exclude_types: ["ETF", "REIT", "ADR"]
  history_period: "2y"
  max_tickers: 3500  # 最大3,500銘柄

# ファンダメンタルズフィルター（新規）
fundamentals:
  enabled: true
  min_eps_growth: 0.25        # 25%
  min_revenue_growth: 0.25    # 25%
  min_operating_margin: 0.15  # 15%（オプション）
  require_qoq_acceleration: true

# バックテスト設定（拡張）
backtest:
  start_date: "2020-01-01"
  end_date: "2025-01-27"
  initial_capital: 10_000
  max_positions: 5
  commission: 0.001
  slippage: 0.001  # 0.1%
  enable_detailed_log: true
```

---

## 実装するファイル

### 新規作成
1. `scripts/update_tickers_extended.py` - 3,500銘柄取得
2. `python/analysis/fundamentals.py` - ファンダ分析
3. `python/backtest/engine.py` - バックテスト
4. `python/backtest/performance.py` - パフォーマンス計測
5. `python/backtest/visualization.py` - グラフ生成

### 既存修正
1. `python/screening/screener.py` - ファンダフィルター統合
2. `python/main.py` - バックテストモード追加
3. `config/params.yaml` - 設定追加

---

## 実行フロー

### ステップ1: 銘柄リスト拡張
```powershell
cd C:\00_mycode\Invest\python
python scripts/update_tickers_extended.py
# → config/tickers.csv に約3,500銘柄保存
```

### ステップ2: ファンダメンタルズ付きスクリーニング
```powershell
python main.py --mode stage2 --with-fundamentals
# → Stage 2 + ファンダ条件を満たす銘柄を抽出
```

### ステップ3: バックテスト実行
```powershell
python main.py --mode backtest --start 2020-01-01 --end 2025-01-27
# → 過去5年のパフォーマンスを計測
```

---

## 期待される結果

### スクリーニング結果
```
Total tickers: 3,500
Stage 2 candidates: 150-300（相場次第）
With Fundamentals: 50-100
With VCP: 10-30
```

### バックテスト結果（期待値）
```
CAGR: 15-25%（ミネルヴィニ戦略の実績）
Max DD: 15-25%
Sharpe Ratio: 1.5-2.5
Win Rate: 55-65%
```

---

## コーディング規約

- 全てPython 3.11+
- 型ヒント必須
- docstring必須（Google形式）
- loguru でログ出力
- pytest でテスト
- 既存コードスタイルを踏襲

---


docs/EXPANSION_SPEC.mdファイルを読んで、
タスク1から順番に実装して。
