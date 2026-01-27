# 株式投資自動化システム - 完全仕様書

## プロジェクト概要
ミネルヴィニのステージ理論に基づいた米国株自動スクリーニングシステム。
TradingView APIでリアルタイムデータを取得し、ステージ判定・VCP検出を自動化。

---

## 技術スタック

### Backend
- Python 3.11+
- TradingView API (tvDatafeed ライブラリ)
- pandas, numpy
- PyYAML (設定管理)

### Frontend（Phase 2）
- Electron + Vite + React + TypeScript + Tailwind CSS
- 既存プロジェクト: C:\00_mycode\Invest

---

## 開発フェーズ

### Phase 1: Python実装（最優先）
1. TradingView API連携
2. ステージ判定ロジック
3. VCP検出ロジック
4. CSV出力
5. バックテスト

### Phase 2: Electron統合
1. PythonスクリプトをElectronから実行
2. CSV読み込み・表示
3. UI改善

---

## ディレクトリ構造
```
Invest/
├── python/
│   ├── data/
│   │   └── fetcher.py              # TradingView API データ取得
│   ├── analysis/
│   │   ├── stage_detector.py       # ステージ判定
│   │   ├── vcp_detector.py         # VCP検出
│   │   └── indicators.py           # MA, RS, ATR等の計算
│   ├── screening/
│   │   └── screener.py             # スクリーニング統合
│   ├── backtest/
│   │   └── engine.py               # バックテスト
│   ├── utils/
│   │   ├── helpers.py              # 共通関数
│   │   └── logger.py               # ログ管理
│   ├── config/
│   │   └── params.yaml             # パラメータ設定
│   ├── output/
│   │   └── screening_results.csv   # 出力先
│   └── main.py                     # エントリーポイント
├── docs/
│   └── trade_rules.md              # トレードルール詳細
├── tests/
│   ├── test_stage_detector.py
│   ├── test_vcp_detector.py
│   └── test_indicators.py
└── requirements.txt
```

---

## データソース仕様

### TradingView API
- ライブラリ: `tvDatafeed` (非公式)
- リアルタイムデータ取得
- 対象: 米国株（NYSE, NASDAQ）

### インストール
```bash
pip install tvdatafeed pandas numpy pyyaml
```

### 基本的な使い方
```python
from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed()
# AAPLの日足データを500本取得
data = tv.get_hist(
    symbol='AAPL',
    exchange='NASDAQ',
    interval=Interval.in_daily,
    n_bars=500
)
```

---

## スクリーニング仕様

### 対象銘柄
- 市場: NYSE + NASDAQ
- 時価総額: 20億ドル以上（中型株以上）
- 最低株価: 5ドル以上
- 最低出来高: 50万株/日以上
- 除外: ETF, REIT, ADR

### 取得する銘柄リスト
```python
# S&P 500 + NASDAQ 100 + Russell 2000の一部
# 合計約1,500銘柄を対象
# 銘柄リストはCSVで管理: config/tickers.csv
```

---

## パラメータ設定（config/params.yaml）
```yaml
# データソース設定
data:
  source: "tradingview"
  exchanges: ["NYSE", "NASDAQ"]
  min_market_cap: 2_000_000_000  # 20億ドル
  min_price: 5.0
  min_volume: 500_000
  exclude_types: ["ETF", "REIT", "ADR"]
  history_days: 252  # 52週 = 252営業日

# ベンチマーク
benchmark:
  symbol: "SPY"  # S&P 500 ETF
  exchange: "NYSE"

# ステージ判定パラメータ
stage:
  sma_periods: [50, 150, 200]
  min_price_above_52w_low: 1.30      # 52週安値から30%以上
  max_distance_from_52w_high: 0.75   # 52週高値の75%以上
  min_slope_200_days: 20              # 200日MAの最小上昇日数
  rs_min_rating: 70
  rs_new_high_required: true

# VCP検出パラメータ
vcp:
  base_period_min: 35
  base_period_max: 65
  contraction_sequence: [0.25, 0.15, 0.08, 0.05]
  last_contraction_max: 0.10
  dryup_vol_ratio: 0.6
  breakout_vol_ratio: 1.5
  pivot_min_high_52w_ratio: 0.95

# エントリー条件
entry:
  buy_zone_pct: 0.03                 # ピボットから3%以内
  breakout_vol_ratio: 1.5            # 出来高が50日平均の1.5倍以上

# リスク管理
risk:
  risk_per_trade: 0.0075             # 0.75%（資産の）
  max_loss_hard: 0.10                # 10%
  initial_stop_max: 0.07             # 7%
  pivot_buffer_atr: 0.5

# エグジット条件
exit:
  partial_sell_bb_ratio: 0.25        # BB上限で25%利確
  sma_50_exit: true                  # 50日MA割れで全撤退
  trail_stop_atr: 2.0

# バックテスト設定
backtest:
  start_date: "2020-01-01"
  end_date: "2025-01-27"
  initial_capital: 1_000_000         # 100万円 = $10,000相当
  max_positions: 5                   # 同時保有最大5銘柄
  commission: 0.001                  # 0.1%

# 出力設定
output:
  csv_path: "output/screening_results.csv"
  log_level: "INFO"
```

---

## 実装要件

### 1. データ取得（python/data/fetcher.py）
```python
from tvDatafeed import TvDatafeed, Interval
from typing import List, Dict
import pandas as pd

class TradingViewFetcher:
    """TradingView APIからデータ取得"""
    
    def __init__(self):
        self.tv = TvDatafeed()
    
    def fetch_data(
        self,
        symbol: str,
        exchange: str,
        n_bars: int = 500
    ) -> pd.DataFrame:
        """
        指定銘柄のデータ取得
        
        Args:
            symbol: ティッカーシンボル（例: "AAPL"）
            exchange: 取引所（例: "NASDAQ"）
            n_bars: 取得本数（デフォルト500）
        
        Returns:
            DataFrame with columns: [open, high, low, close, volume]
        """
        pass
    
    def fetch_multiple(
        self,
        tickers: List[str],
        exchange_map: Dict[str, str]
    ) -> Dict[str, pd.DataFrame]:
        """
        複数銘柄のデータを一括取得
        
        Args:
            tickers: ティッカーリスト
            exchange_map: {ticker: exchange} のマッピング
        
        Returns:
            {ticker: DataFrame} の辞書
        """
        pass
```

---

### 2. テクニカル指標計算（python/analysis/indicators.py）
```python
import pandas as pd
import numpy as np

def calculate_sma(data: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
    """移動平均線を計算"""
    pass

def calculate_52w_high_low(data: pd.DataFrame) -> tuple:
    """52週高値・安値を計算"""
    pass

def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """ATR（Average True Range）を計算"""
    pass

def calculate_rs_line(
    stock_data: pd.DataFrame,
    benchmark_data: pd.DataFrame
) -> pd.Series:
    """
    相対力指標（RS Line）を計算
    RS = (株価 / ベンチマーク価格)
    """
    pass

def is_rs_new_high(rs_line: pd.Series, window: int = 252) -> bool:
    """RSラインが52週高値更新しているか判定"""
    pass

def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0
) -> Dict[str, pd.Series]:
    """ボリンジャーバンドを計算"""
    pass
```

---

### 3. ステージ判定（python/analysis/stage_detector.py）
```python
import pandas as pd
from typing import Dict, List

class StageDetector:
    """ステージ理論に基づく判定"""
    
    def __init__(self, params: Dict):
        self.params = params
    
    def detect_stage(
        self,
        data: pd.DataFrame,
        rs_line: pd.Series
    ) -> Dict:
        """
        ステージを判定
        
        Returns:
            {
                'stage': 2,
                'meets_criteria': True,
                'details': {
                    'price_above_sma50': True,
                    'sma50_above_sma150': True,
                    ...
                }
            }
        """
        pass
    
    def check_stage2_conditions(
        self,
        data: pd.DataFrame,
        rs_line: pd.Series
    ) -> Dict[str, bool]:
        """
        Stage 2の7条件をチェック
        
        1. Close > SMA_50 > SMA_150 > SMA_200
        2. SMA_200が上昇トレンド（20日以上）
        3. Close ≥ 52週安値 × 1.30
        4. Close ≥ 52週高値 × 0.75
        5. SMA_50 > SMA_150 かつ SMA_50 > SMA_200
        6. RS ≥ 70 または RSライン新高値
        7. 出来高 ≥ 50万株/日
        """
        pass
```

---

### 4. VCP検出（python/analysis/vcp_detector.py）
```python
import pandas as pd
from typing import Dict, List, Optional

class VCPDetector:
    """Volatility Contraction Pattern 検出"""
    
    def __init__(self, params: Dict):
        self.params = params
    
    def detect_vcp(
        self,
        data: pd.DataFrame
    ) -> Optional[Dict]:
        """
        VCPパターンを検出
        
        Returns:
            {
                'has_vcp': True,
                'pivot': 187.50,
                'base_start': '2024-11-01',
                'base_end': '2025-01-15',
                'contractions': [0.28, 0.18, 0.10, 0.06],
                'dryup_confirmed': True,
                'entry_price': 188.12,
                'stop_price': 182.30
            }
            または None（VCPなし）
        """
        pass
    
    def find_base(
        self,
        data: pd.DataFrame
    ) -> Optional[tuple]:
        """
        ベース期間を検出（35-65日）
        
        Returns:
            (start_idx, end_idx) または None
        """
        pass
    
    def extract_swings(
        self,
        data: pd.DataFrame,
        base_start: int,
        base_end: int
    ) -> List[Dict]:
        """
        スイング高安を抽出
        
        Returns:
            [
                {'type': 'high', 'price': 185.50, 'date': '2024-12-01'},
                {'type': 'low', 'price': 178.20, 'date': '2024-12-05'},
                ...
            ]
        """
        pass
    
    def check_contraction_sequence(
        self,
        swings: List[Dict]
    ) -> Optional[List[float]]:
        """
        収縮パターンをチェック
        
        Returns:
            [0.28, 0.18, 0.10, 0.06] のような収縮率リスト
            または None（条件不合格）
        """
        pass
    
    def check_dryup(
        self,
        data: pd.DataFrame,
        base_end: int
    ) -> bool:
        """
        ドライアップ（出来高枯渇）を確認
        
        条件: 10日平均出来高 ≤ 50日平均 × 0.6
        """
        pass
    
    def calculate_pivot(
        self,
        data: pd.DataFrame,
        base_start: int,
        base_end: int
    ) -> float:
        """
        ピボット価格を計算（ベース最高値）
        """
        pass
    
    def calculate_stop_price(
        self,
        data: pd.DataFrame,
        pivot: float,
        base_start: int,
        base_end: int
    ) -> float:
        """
        初期ストップ価格を計算
        
        max(
            pivot × 0.97,
            last_contraction_low - 0.5×ATR14
        )
        """
        pass
```

---

### 5. スクリーニング統合（python/screening/screener.py）
```python
import pandas as pd
from typing import List, Dict
from data.fetcher import TradingViewFetcher
from analysis.stage_detector import StageDetector
from analysis.vcp_detector import VCPDetector
from analysis.indicators import *

class Screener:
    """スクリーニング統合クラス"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.fetcher = TradingViewFetcher()
        self.stage_detector = StageDetector(config['stage'])
        self.vcp_detector = VCPDetector(config['vcp'])
    
    def screen(self, tickers: List[str]) -> pd.DataFrame:
        """
        全銘柄をスクリーニング
        
        Returns:
            DataFrame with columns:
            [ticker, stage, rs, has_vcp, pivot, entry_price, stop_price, risk_reward]
        """
        results = []
        
        for ticker in tickers:
            try:
                # データ取得
                data = self.fetcher.fetch_data(ticker, exchange)
                
                # ステージ判定
                stage_result = self.stage_detector.detect_stage(data, rs_line)
                
                if stage_result['stage'] != 2:
                    continue
                
                # VCP検出
                vcp_result = self.vcp_detector.detect_vcp(data)
                
                if vcp_result and vcp_result['has_vcp']:
                    results.append({
                        'ticker': ticker,
                        'stage': 2,
                        'rs': rs_value,
                        'has_vcp': True,
                        'pivot': vcp_result['pivot'],
                        'entry_price': vcp_result['entry_price'],
                        'stop_price': vcp_result['stop_price'],
                        'risk_reward': calculate_risk_reward(...)
                    })
                    
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                continue
        
        return pd.DataFrame(results)
```

---

### 6. メインスクリプト（python/main.py）
```python
import yaml
from screening.screener import Screener
from utils.logger import setup_logger
import pandas as pd

def main():
    # 設定読み込み
    with open('config/params.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # ログ設定
    logger = setup_logger(config['output']['log_level'])
    
    # 銘柄リスト読み込み
    tickers_df = pd.read_csv('config/tickers.csv')
    tickers = tickers_df['ticker'].tolist()
    
    logger.info(f"Starting screening for {len(tickers)} tickers")
    
    # スクリーニング実行
    screener = Screener(config)
    results = screener.screen(tickers)
    
    # CSV出力
    output_path = config['output']['csv_path']
    results.to_csv(output_path, index=False)
    
    logger.info(f"Screening complete. {len(results)} candidates found.")
    logger.info(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()
```

---

## requirements.txt
```txt
tvdatafeed>=2.1.0
pandas>=2.0.0
numpy>=1.24.0
pyyaml>=6.0
pytest>=7.4.0
```

---

## 実装順序

### Step 1: 基盤構築
1. `requirements.txt`作成してライブラリインストール
2. `config/params.yaml`作成
3. `config/tickers.csv`作成（S&P500銘柄リスト）

### Step 2: データ取得
1. `python/data/fetcher.py`実装
2. 1銘柄（例: AAPL）でテスト
3. テストパス後、複数銘柄対応

### Step 3: テクニカル指標
1. `python/analysis/indicators.py`実装
2. SMA, ATR, RSライン等を計算
3. ユニットテスト作成

### Step 4: ステージ判定
1. `python/analysis/stage_detector.py`実装
2. 7条件の完全実装
3. テストケース作成

### Step 5: VCP検出
1. `python/analysis/vcp_detector.py`実装
2. ベース検出、スイング抽出、収縮判定
3. テストケース作成

### Step 6: 統合
1. `python/screening/screener.py`実装
2. `python/main.py`実装
3. CSV出力確認

### Step 7: バックテスト
1. `python/backtest/engine.py`実装
2. 2020-2025期間でテスト
3. パフォーマンス分析

---

## テスト方針

### ユニットテスト
- 各関数の入出力を検証
- エッジケース（欠損値、異常値）のテスト

### 統合テスト
- 実データでのE2Eテスト
- 既知の銘柄（AAPL, MSFT等）で手動検証

### バックテスト検証
- 過去の有名なブレイクアウト銘柄で検証
- 例: TSLA (2020), NVDA (2023), SHOP (2019)

---

## トレードルール詳細

docs/trade_rules.md に記載されたミネルヴィニの戦略を完全に実装する。

特に重視:
- Stage 2の7条件厳守
- VCPの収縮パターン検出
- リスク管理（最大損失7-10%）
- エントリー: ピボットブレイク + 出来高1.5倍
- エグジット: 50日MA割れで全撤退

---

## エラーハンドリング

### データ取得エラー
- TradingView APIのレート制限対応
- 銘柄が見つからない場合はスキップ
- リトライロジック実装

### 計算エラー
- データ不足の場合はスキップ
- 異常値のフィルタリング

---

## 出力フォーマット（CSV）
```csv
ticker,stage,rs,has_vcp,pivot,entry_price,stop_price,risk_pct,risk_reward,last_updated
AAPL,2,92,TRUE,187.50,188.12,182.30,3.1,3.5,2025-01-27 10:30:00
MSFT,2,88,TRUE,378.50,380.00,368.00,3.2,3.2,2025-01-27 10:30:00
NVDA,2,95,TRUE,495.80,498.20,485.50,2.6,4.1,2025-01-27 10:30:00
```

---

## 開発コマンド
```bash
# セットアップ
cd C:\00_mycode\Invest\python
pip install -r requirements.txt

# スクリーニング実行
python main.py

# テスト実行
pytest tests/

# 特定のテスト
pytest tests/test_stage_detector.py -v
```

---

## コーディング規約

### Python
- PEP 8準拠
- 型ヒント必須
- docstring必須（Google形式）
- 関数は1つのことだけ
- クラスは単一責任

### ファイル命名
- スネークケース（例: `stage_detector.py`）
- テストファイルは`test_`プレフィックス

---

## ログ出力
```python
# utils/logger.py
import logging

def setup_logger(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('output/screening.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
```

---

## 重要な注意事項

### TradingView API制限
- 無料版: 1分あたり5リクエスト程度
- Pro版: より緩和されるが依然として制限あり
- 実装時はリクエスト間に0.5-1秒のsleep()を入れる

### データ品質
- 欠損値のチェック必須
- 異常値（価格0、出来高0等）の除外

### パフォーマンス
- 1,500銘柄のスクリーニングに約30-60分かかる想定
- 並列化は将来検討（Phase 2）

---

## Phase 2でのElectron統合

Pythonが完成後、以下を実装:

1. Electronから`python main.py`を実行
2. CSV読み込み
3. UIに結果表示
4. チャート表示（TradingView埋め込み）
5. リアルタイム更新（1日1回自動実行）

---

## 成功基準

### Phase 1完了条件
- [ ] 1,500銘柄のスクリーニングが動作
- [ ] Stage 2候補が50-150銘柄抽出される
- [ ] VCP候補が10-30銘柄検出される
- [ ] CSV出力が正常
- [ ] バックテストで年率15%以上
- [ ] 全ユニットテストパス

