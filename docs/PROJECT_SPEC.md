# 株式投資自動化システム - 完全仕様書（yfinance版）

## プロジェクト概要
ミネルヴィニのステージ理論に基づいた米国株自動スクリーニングシステム。
Yahoo Finance（yfinance）でデータを取得し、ステージ判定・VCP検出を自動化。

---

## 技術スタック

### Backend
- Python 3.11+
- yfinance（Yahoo Finance API）
- pandas, numpy
- PyYAML（設定管理）
- pytest（テスト）

### Frontend（Phase 2）
- Electron + Vite + React + TypeScript + Tailwind CSS
- 既存プロジェクト: `C:\00_mycode\Invest`

---

## 開発フェーズ

### Phase 1: Python実装（最優先）
1. yfinance API連携
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
│   │   └── fetcher.py              # yfinance データ取得
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
│   │   ├── params.yaml             # パラメータ設定
│   │   └── tickers.csv             # スクリーニング対象銘柄リスト
│   ├── output/
│   │   └── screening_results.csv   # 出力先
│   └── main.py                     # エントリーポイント
├── docs/
│   ├── PROJECT_SPEC.md             # 本ドキュメント
│   └── trade_rules.md              # トレードルール詳細
├── tests/
│   ├── test_stage_detector.py
│   ├── test_vcp_detector.py
│   └── test_indicators.py
└── requirements.txt
```

---

## データソース仕様

### Yahoo Finance（yfinance）

**選定理由**
- ✅ 完全無料
- ✅ 認証不要（APIキー不要）
- ✅ Yahoo Finance公式データ
- ✅ 安定性が高い
- ✅ 実装が簡単
- ⚠️ 15-20分遅延（日足戦略では問題なし）

**対象市場**
- NYSE（ニューヨーク証券取引所）
- NASDAQ（ナスダック）

**取得可能データ**
- OHLCV（始値、高値、安値、終値、出来高）
- 調整後終値（株式分割・配当調整済み）
- 企業情報（時価総額、セクター等）

---

## インストール

### requirements.txt
```txt
# データ取得
yfinance>=0.2.28

# データ処理
pandas>=2.0.0
numpy>=1.24.0

# 設定管理
pyyaml>=6.0

# テスト
pytest>=7.4.0
pytest-cov>=4.1.0

# ログ
loguru>=0.7.0

# 進捗表示
tqdm>=4.66.0
```

### インストール手順
```bash
cd C:\00_mycode\Invest\python
pip install -r requirements.txt
```

---

## スクリーニング仕様

### 対象銘柄

**市場**
- NYSE + NASDAQ

**フィルター条件**
- 時価総額：20億ドル以上（中型株以上）
- 最低株価：5ドル以上
- 最低出来高：50万株/日以上
- 除外：ETF, REIT, ADR, 低位株

**対象銘柄数の目安**
- S&P 500: 約500銘柄
- NASDAQ 100: 約100銘柄
- その他主要株: 約900銘柄
- **合計：約1,500銘柄**

### 銘柄リスト管理

`config/tickers.csv`で管理：
```csv
ticker,exchange,sector,market_cap
AAPL,NASDAQ,Technology,3000000000000
MSFT,NASDAQ,Technology,2800000000000
NVDA,NASDAQ,Technology,1200000000000
GOOGL,NASDAQ,Technology,1800000000000
META,NASDAQ,Technology,900000000000
...
```

**取得方法**
- S&P 500リスト：Wikipedia等から取得
- NASDAQ 100リスト：公式サイトから取得
- 時価総額フィルター：yfinanceの`.info`で取得

---

## パラメータ設定（config/params.yaml）
```yaml
# データソース設定
data:
  source: "yfinance"
  min_market_cap: 2_000_000_000  # 20億ドル
  min_price: 5.0
  min_volume: 500_000
  exclude_types: ["ETF", "REIT", "ADR"]
  history_period: "2y"  # 2年分のデータ取得

# ベンチマーク
benchmark:
  symbol: "SPY"  # S&P 500 ETF

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
  initial_capital: 10_000            # $10,000（約100万円相当）
  max_positions: 5                   # 同時保有最大5銘柄
  commission: 0.001                  # 0.1%

# 出力設定
output:
  csv_path: "output/screening_results.csv"
  log_path: "output/screening.log"
  log_level: "INFO"

# パフォーマンス設定
performance:
  max_workers: 4          # 並列処理のワーカー数
  request_delay: 0.5      # yfinanceリクエスト間の待機時間（秒）
  retry_attempts: 3       # リトライ回数
  timeout: 30             # タイムアウト（秒）
```

---

## 実装要件

### 1. データ取得（python/data/fetcher.py）
```python
"""
yfinance を使用したデータ取得モジュール
"""
import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from loguru import logger
import time

class YahooFinanceFetcher:
    """Yahoo Finance (yfinance) データ取得クラス"""
    
    def __init__(self, request_delay: float = 0.5):
        """
        初期化
        
        Args:
            request_delay: リクエスト間の待機時間（秒）
        """
        self.request_delay = request_delay
    
    def fetch_data(
        self,
        symbol: str,
        period: str = "2y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        単一銘柄のデータ取得
        
        Args:
            symbol: ティッカーシンボル（例: "AAPL"）
            period: 取得期間（"1y", "2y", "5y", "max"）
            interval: 時間軸（"1d", "1wk", "1mo"）
        
        Returns:
            DataFrame with columns: [Open, High, Low, Close, Volume, Adj Close]
            取得失敗時はNone
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"{symbol}: No data available")
                return None
            
            # カラム名を標準化
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            
            # 必要なカラムのみ残す
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            data = data[required_cols]
            
            logger.info(f"{symbol}: Fetched {len(data)} bars")
            
            # レート制限対策
            time.sleep(self.request_delay)
            
            return data
            
        except Exception as e:
            logger.error(f"{symbol}: Error fetching data - {e}")
            return None
    
    def fetch_multiple(
        self,
        symbols: List[str],
        period: str = "2y",
        show_progress: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        複数銘柄のデータを一括取得
        
        Args:
            symbols: ティッカーリスト
            period: 取得期間
            show_progress: 進捗表示
        
        Returns:
            {symbol: DataFrame} の辞書
        """
        results = {}
        
        if show_progress:
            from tqdm import tqdm
            symbols = tqdm(symbols, desc="Fetching data")
        
        for symbol in symbols:
            data = self.fetch_data(symbol, period=period)
            if data is not None:
                results[symbol] = data
        
        logger.info(f"Successfully fetched {len(results)}/{len(symbols)} symbols")
        return results
    
    def get_ticker_info(self, symbol: str) -> Optional[Dict]:
        """
        銘柄情報を取得
        
        Args:
            symbol: ティッカーシンボル
        
        Returns:
            銘柄情報の辞書（時価総額、セクター等）
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'current_price': info.get('currentPrice', 0),
                'average_volume': info.get('averageVolume', 0),
            }
            
        except Exception as e:
            logger.error(f"{symbol}: Error fetching info - {e}")
            return None
    
    def filter_by_market_cap(
        self,
        symbols: List[str],
        min_market_cap: float
    ) -> List[str]:
        """
        時価総額でフィルタリング
        
        Args:
            symbols: ティッカーリスト
            min_market_cap: 最低時価総額
        
        Returns:
            フィルタ後のティッカーリスト
        """
        filtered = []
        
        for symbol in symbols:
            info = self.get_ticker_info(symbol)
            if info and info['market_cap'] >= min_market_cap:
                filtered.append(symbol)
                logger.debug(f"{symbol}: Market cap ${info['market_cap']:,.0f}")
            
            time.sleep(self.request_delay)
        
        logger.info(f"Filtered: {len(filtered)}/{len(symbols)} symbols above ${min_market_cap:,.0f}")
        return filtered
```

---

### 2. テクニカル指標計算（python/analysis/indicators.py）
```python
"""
テクニカル指標計算モジュール
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

def calculate_sma(data: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
    """
    移動平均線（SMA）を計算
    
    Args:
        data: 株価データ
        periods: 期間リスト（例: [50, 150, 200]）
    
    Returns:
        SMAカラムを追加したDataFrame
    """
    result = data.copy()
    
    for period in periods:
        col_name = f'sma_{period}'
        result[col_name] = result['close'].rolling(window=period).mean()
    
    return result

def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
    """
    指数移動平均線（EMA）を計算
    
    Args:
        data: 株価データ
        period: 期間
    
    Returns:
        EMA Series
    """
    return data['close'].ewm(span=period, adjust=False).mean()

def calculate_52w_high_low(data: pd.DataFrame) -> Tuple[float, float]:
    """
    52週高値・安値を計算
    
    Args:
        data: 株価データ（最低252営業日必要）
    
    Returns:
        (52週高値, 52週安値)
    """
    lookback = min(252, len(data))  # 252営業日 = 約52週
    
    high_52w = data['high'].tail(lookback).max()
    low_52w = data['low'].tail(lookback).min()
    
    return high_52w, low_52w

def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    ATR（Average True Range）を計算
    
    Args:
        data: 株価データ
        period: 期間（デフォルト14）
    
    Returns:
        ATR Series
    """
    high = data['high']
    low = data['low']
    close = data['close']
    
    # True Range計算
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR = TRの移動平均
    atr = true_range.rolling(window=period).mean()
    
    return atr

def calculate_rs_line(
    stock_data: pd.DataFrame,
    benchmark_data: pd.DataFrame
) -> pd.Series:
    """
    相対力指標（RS Line）を計算
    
    RS = (株価 / ベンチマーク価格)
    
    Args:
        stock_data: 個別株データ
        benchmark_data: ベンチマーク（S&P500等）データ
    
    Returns:
        RS Line Series
    """
    # インデックスを揃える
    common_index = stock_data.index.intersection(benchmark_data.index)
    
    stock_close = stock_data.loc[common_index, 'close']
    bench_close = benchmark_data.loc[common_index, 'close']
    
    rs_line = stock_close / bench_close
    
    return rs_line

def is_rs_new_high(rs_line: pd.Series, window: int = 252) -> bool:
    """
    RSラインが52週高値更新しているか判定
    
    Args:
        rs_line: RS Line
        window: 判定期間（デフォルト252営業日）
    
    Returns:
        True: 新高値更新
        False: 未更新
    """
    if len(rs_line) < window:
        return False
    
    recent_high = rs_line.tail(window).max()
    current_value = rs_line.iloc[-1]
    
    # 現在値が期間内最高値の95%以上なら新高値とみなす
    return current_value >= recent_high * 0.95

def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0
) -> Dict[str, pd.Series]:
    """
    ボリンジャーバンドを計算
    
    Args:
        data: 株価データ
        period: 期間（デフォルト20）
        std_dev: 標準偏差倍率（デフォルト2.0）
    
    Returns:
        {'middle': SMA, 'upper': 上限, 'lower': 下限}
    """
    middle = data['close'].rolling(window=period).mean()
    std = data['close'].rolling(window=period).std()
    
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return {
        'middle': middle,
        'upper': upper,
        'lower': lower
    }

def calculate_volume_ma(data: pd.DataFrame, period: int) -> pd.Series:
    """
    出来高移動平均を計算
    
    Args:
        data: 株価データ
        period: 期間
    
    Returns:
        出来高移動平均 Series
    """
    return data['volume'].rolling(window=period).mean()

def calculate_all_indicators(
    data: pd.DataFrame,
    benchmark_data: pd.DataFrame
) -> pd.DataFrame:
    """
    全てのテクニカル指標を一括計算
    
    Args:
        data: 株価データ
        benchmark_data: ベンチマークデータ
    
    Returns:
        全指標を含むDataFrame
    """
    result = data.copy()
    
    # 移動平均線
    result = calculate_sma(result, [50, 150, 200])
    result['ema_21'] = calculate_ema(result, 21)
    
    # ATR
    result['atr_14'] = calculate_atr(result, 14)
    
    # RS Line
    result['rs_line'] = calculate_rs_line(result, benchmark_data)
    
    # ボリンジャーバンド
    bb = calculate_bollinger_bands(result)
    result['bb_middle'] = bb['middle']
    result['bb_upper'] = bb['upper']
    result['bb_lower'] = bb['lower']
    
    # 出来高MA
    result['volume_ma_10'] = calculate_volume_ma(result, 10)
    result['volume_ma_50'] = calculate_volume_ma(result, 50)
    
    return result
```

---

### 3. ステージ判定（python/analysis/stage_detector.py）
```python
"""
ステージ判定モジュール
"""
import pandas as pd
from typing import Dict
from loguru import logger

class StageDetector:
    """ステージ理論に基づく判定クラス"""
    
    def __init__(self, params: Dict):
        """
        初期化
        
        Args:
            params: stage判定パラメータ
        """
        self.params = params
    
    def detect_stage(
        self,
        data: pd.DataFrame,
        rs_line: pd.Series
    ) -> Dict:
        """
        ステージを判定
        
        Args:
            data: 全指標を含む株価データ
            rs_line: RS Line
        
        Returns:
            {
                'stage': 2,
                'meets_criteria': True,
                'details': {...}
            }
        """
        # Stage 2条件チェック
        conditions = self.check_stage2_conditions(data, rs_line)
        
        # 全条件を満たすか
        meets_all = all(conditions.values())
        
        # ステージ判定
        if meets_all:
            stage = 2
        elif self._is_stage4(data):
            stage = 4
        elif self._is_stage3(data):
            stage = 3
        else:
            stage = 1
        
        return {
            'stage': stage,
            'meets_criteria': meets_all,
            'details': conditions
        }
    
    def check_stage2_conditions(
        self,
        data: pd.DataFrame,
        rs_line: pd.Series
    ) -> Dict[str, bool]:
        """
        Stage 2の7条件をチェック
        
        Returns:
            各条件の真偽値辞書
        """
        latest = data.iloc[-1]
        
        # 52週高値・安値
        high_52w, low_52w = self._get_52w_high_low(data)
        
        # 200日MAの傾き
        ma200_slope = self._calculate_ma200_slope(data)
        
        conditions = {
            # 1. Close > SMA_50 > SMA_150 > SMA_200
            'price_above_sma50': latest['close'] > latest['sma_50'],
            'sma50_above_sma150': latest['sma_50'] > latest['sma_150'],
            'sma150_above_sma200': latest['sma_150'] > latest['sma_200'],
            
            # 2. 200日MAが上昇トレンド
            'ma200_uptrend': ma200_slope > 0,
            
            # 3. 52週安値から30%以上上昇
            'above_52w_low': latest['close'] >= low_52w * self.params['min_price_above_52w_low'],
            
            # 4. 52週高値の75%以上
            'near_52w_high': latest['close'] >= high_52w * self.params['max_distance_from_52w_high'],
            
            # 5. 50日MAが150日・200日MAの上
            'ma50_above_ma150_200': (
                latest['sma_50'] > latest['sma_150'] and
                latest['sma_50'] > latest['sma_200']
            ),
            
            # 6. RS新高値
            'rs_new_high': self._check_rs_strength(rs_line),
            
            # 7. 流動性
            'sufficient_volume': latest['volume_ma_50'] >= self.params['min_volume']
        }
        
        return conditions
    
    def _get_52w_high_low(self, data: pd.DataFrame) -> tuple:
        """52週高値・安値を取得"""
        lookback = min(252, len(data))
        high_52w = data['high'].tail(lookback).max()
        low_52w = data['low'].tail(lookback).min()
        return high_52w, low_52w
    
    def _calculate_ma200_slope(self, data: pd.DataFrame) -> float:
        """200日MAの傾きを計算"""
        min_days = self.params['min_slope_200_days']
        
        if len(data) < min_days + 1:
            return 0
        
        ma200_current = data['sma_200'].iloc[-1]
        ma200_past = data['sma_200'].iloc[-(min_days + 1)]
        
        slope = ma200_current - ma200_past
        return slope
    
    def _check_rs_strength(self, rs_line: pd.Series) -> bool:
        """RS強度をチェック"""
        if len(rs_line) < 252:
            return False
        
        # RSラインが52週高値更新
        recent_high = rs_line.tail(252).max()
        current = rs_line.iloc[-1]
        
        return current >= recent_high * 0.95
    
    def _is_stage4(self, data: pd.DataFrame) -> bool:
        """Stage 4（下落期）判定"""
        latest = data.iloc[-1]
        
        return (
            latest['close'] < latest['sma_200'] and
            self._calculate_ma200_slope(data) < 0
        )
    
    def _is_stage3(self, data: pd.DataFrame) -> bool:
        """Stage 3（天井期）判定"""
        latest = data.iloc[-1]
        ma200_slope = self._calculate_ma200_slope(data)
        
        # 200日MAが横ばい
        return abs(ma200_slope) < (latest['sma_200'] * 0.01)
```

---

### 4. VCP検出（python/analysis/vcp_detector.py）
```python
"""
VCP（Volatility Contraction Pattern）検出モジュール
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from loguru import logger

class VCPDetector:
    """VCP検出クラス"""
    
    def __init__(self, params: Dict):
        """
        初期化
        
        Args:
            params: VCP検出パラメータ
        """
        self.params = params
    
    def detect_vcp(self, data: pd.DataFrame) -> Optional[Dict]:
        """
        VCPパターンを検出
        
        Args:
            data: 全指標を含む株価データ
        
        Returns:
            VCP情報の辞書、または None
        """
        # ベース期間を検出
        base = self.find_base(data)
        if base is None:
            return None
        
        base_start, base_end = base
        
        # スイング高安を抽出
        swings = self.extract_swings(data, base_start, base_end)
        if len(swings) < 4:  # 最低2回の上下動が必要
            return None
        
        # 収縮シーケンスをチェック
        contractions = self.check_contraction_sequence(swings)
        if contractions is None:
            return None
        
        # ドライアップ確認
        dryup = self.check_dryup(data, base_end)
        
        # ピボット計算
        pivot = self.calculate_pivot(data, base_start, base_end)
        
        # 52週高値チェック
        high_52w, _ = self._get_52w_high_low(data)
        if pivot < high_52w * self.params['pivot_min_high_52w_ratio']:
            logger.debug("Pivot too far from 52w high")
            return None
        
        # ストップ価格計算
        stop = self.calculate_stop_price(data, pivot, base_start, base_end)
        
        # エントリー価格（ピボット突破）
        entry = pivot * 1.01  # ピボット+1%
        
        return {
            'has_vcp': True,
            'pivot': pivot,
            'base_start': data.index[base_start],
            'base_end': data.index[base_end],
            'contractions': contractions,
            'dryup_confirmed': dryup,
            'entry_price': entry,
            'stop_price': stop,
            'risk_pct': (entry - stop) / entry
        }
    
    def find_base(self, data: pd.DataFrame) -> Optional[Tuple[int, int]]:
        """
        ベース期間を検出（35-65日）
        
        Returns:
            (start_idx, end_idx) または None
        """
        min_period = self.params['base_period_min']
        max_period = self.params['base_period_max']
        
        # 最新から遡ってベースを探す
        for period in range(max_period, min_period - 1, -1):
            if len(data) < period:
                continue
            
            base_data = data.tail(period)
            
            # ベースの条件チェック
            if self._is_valid_base(base_data):
                start_idx = len(data) - period
                end_idx = len(data) - 1
                return (start_idx, end_idx)
        
        return None
    
    def _is_valid_base(self, base_data: pd.DataFrame) -> bool:
        """ベースが有効か判定"""
        # 価格レンジの計算
        price_range = (base_data['high'].max() - base_data['low'].min()) / base_data['close'].mean()
        
        # レンジが適切か（10-40%程度）
        if price_range < 0.10 or price_range > 0.40:
            return False
        
        # 出来高が十分か
        if base_data['volume'].mean() < 100_000:
            return False
        
        return True
    
    def extract_swings(
        self,
        data: pd.DataFrame,
        base_start: int,
        base_end: int
    ) -> List[Dict]:
        """
        スイング高安を抽出
        
        Returns:
            [{'type': 'high'/'low', 'price': float, 'idx': int}, ...]
        """
        base_data = data.iloc[base_start:base_end + 1].copy()
        swings = []
        
        # 簡易的なピーク・ボトム検出
        window = 5
        
        for i in range(window, len(base_data) - window):
            # 高値判定
            if base_data['high'].iloc[i] == base_data['high'].iloc[i - window:i + window + 1].max():
                swings.append({
                    'type': 'high',
                    'price': base_data['high'].iloc[i],
                    'idx': base_start + i
                })
            
            # 安値判定
            if base_data['low'].iloc[i] == base_data['low'].iloc[i - window:i + window + 1].min():
                swings.append({
                    'type': 'low',
                    'price': base_data['low'].iloc[i],
                    'idx': base_start + i
                })
        
        # 時系列順にソート
        swings.sort(key=lambda x: x['idx'])
        
        return swings
    
    def check_contraction_sequence(self, swings: List[Dict]) -> Optional[List[float]]:
        """
        収縮シーケンスをチェック
        
        Returns:
            収縮率リスト、または None
        """
        # 高値→安値→高値のペアを抽出
        pullbacks = []
        
        for i in range(len(swings) - 2):
            if (swings[i]['type'] == 'high' and
                swings[i + 1]['type'] == 'low' and
                swings[i + 2]['type'] == 'high'):
                
                high1 = swings[i]['price']
                low = swings[i + 1]['price']
                high2 = swings[i + 2]['price']
                
                # 押し幅の計算
                pullback_pct = (high1 - low) / high1
                pullbacks.append(pullback_pct)
        
        if len(pullbacks) < 3:
            return None
        
        # 収縮パターンの確認（逓減しているか）
        for i in range(len(pullbacks) - 1):
            if pullbacks[i + 1] >= pullbacks[i]:
                return None  # 収縮していない
        
        # 最後の収縮が10%以下か
        if pullbacks[-1] > self.params['last_contraction_max']:
            return None
        
        return pullbacks
    
    def check_dryup(self, data: pd.DataFrame, base_end: int) -> bool:
        """
        ドライアップ（出来高枯渇）を確認
        
        Args:
            data: 株価データ
            base_end: ベース終了位置
        
        Returns:
            True: ドライアップ確認
        """
        if base_end < 50:
            return False
        
        recent_data = data.iloc[base_end - 10:base_end + 1]
        
        vol_ma_10 = recent_data['volume'].mean()
        vol_ma_50 = data.iloc[base_end - 50:base_end + 1]['volume'].mean()
        
        ratio = vol_ma_10 / vol_ma_50
        
        return ratio <= self.params['dryup_vol_ratio']
    
    def calculate_pivot(
        self,
        data: pd.DataFrame,
        base_start: int,
        base_end: int
    ) -> float:
        """
        ピボット価格を計算（ベース最高値）
        """
        base_data = data.iloc[base_start:base_end + 1]
        pivot = base_data['high'].max()
        return pivot
    
    def calculate_stop_price(
        self,
        data: pd.DataFrame,
        pivot: float,
        base_start: int,
        base_end: int
    ) -> float:
        """
        初期ストップ価格を計算
        """
        base_data = data.iloc[base_start:base_end + 1]
        
        # 候補1: ピボット-3%
        stop1 = pivot * 0.97
        
        # 候補2: 最後の収縮安値 - ATRバッファ
        last_low = base_data.tail(10)['low'].min()
        atr = data.iloc[base_end]['atr_14']
        stop2 = last_low - (self.params.get('pivot_buffer_atr', 0.5) * atr)
        
        # より高い方（リスクが小さい方）
        stop_price = max(stop1, stop2)
        
        return stop_price
    
    def _get_52w_high_low(self, data: pd.DataFrame) -> Tuple[float, float]:
        """52週高値・安値を取得"""
        lookback = min(252, len(data))
        high_52w = data['high'].tail(lookback).max()
        low_52w = data['low'].tail(lookback).min()
        return high_52w, low_52w
```

---

### 5. スクリーニング統合（python/screening/screener.py）
```python
"""
スクリーニング統合モジュール
"""
import pandas as pd
from typing import List, Dict
from loguru import logger
from tqdm import tqdm

from data.fetcher import YahooFinanceFetcher
from analysis.stage_detector import StageDetector
from analysis.vcp_detector import VCPDetector
from analysis.indicators import calculate_all_indicators

class Screener:
    """スクリーニング統合クラス"""
    
    def __init__(self, config: Dict):
        """
        初期化
        
        Args:
            config: 設定辞書（params.yamlから読み込み）
        """
        self.config = config
        self.fetcher = YahooFinanceFetcher(
            request_delay=config['performance']['request_delay']
        )
        self.stage_detector = StageDetector(config['stage'])
        self.vcp_detector = VCPDetector(config['vcp'])
    
    def screen(self, tickers: List[str]) -> pd.DataFrame:
        """
        全銘柄をスクリーニング
        
        Args:
            tickers: ティッカーリスト
        
        Returns:
            スクリーニング結果DataFrame
        """
        results = []
        
        # ベンチマークデータ取得
        logger.info("Fetching benchmark data (SPY)...")
        benchmark_symbol = self.config['benchmark']['symbol']
        benchmark_data = self.fetcher.fetch_data(
            benchmark_symbol,
            period=self.config['data']['history_period']
        )
        
        if benchmark_data is None:
            logger.error("Failed to fetch benchmark data")
            return pd.DataFrame()
        
        # 各銘柄を処理
        logger.info(f"Screening {len(tickers)} tickers...")
        
        for ticker in tqdm(tickers, desc="Screening"):
            try:
                result = self._process_ticker(ticker, benchmark_data)
                if result:
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"{ticker}: Error - {e}")
                continue
        
        # DataFrame化
        if results:
            df = pd.DataFrame(results)
            logger.info(f"Found {len(df)} Stage 2 candidates")
            return df
        else:
            logger.warning("No candidates found")
            return pd.DataFrame()
    
    def _process_ticker(
        self,
        ticker: str,
        benchmark_data: pd.DataFrame
    ) -> Optional[Dict]:
        """
        個別銘柄を処理
        
        Returns:
            スクリーニング結果、または None
        """
        # データ取得
        data = self.fetcher.fetch_data(
            ticker,
            period=self.config['data']['history_period']
        )
        
        if data is None or len(data) < 252:
            return None
        
        # テクニカル指標計算
        data = calculate_all_indicators(data, benchmark_data)
        
        # ステージ判定
        stage_result = self.stage_detector.detect_stage(
            data,
            data['rs_line']
        )
        
        if stage_result['stage'] != 2:
            return None
        
        # VCP検出
        vcp_result = self.vcp_detector.detect_vcp(data)
        
        if vcp_result is None:
            return None
        
        # リスク検証
        risk_pct = vcp_result['risk_pct']
        if risk_pct > self.config['risk']['initial_stop_max']:
            logger.debug(f"{ticker}: Risk too high ({risk_pct:.2%})")
            return None
        
        # リスク・リワード計算
        entry = vcp_result['entry_price']
        stop = vcp_result['stop_price']
        target = entry * 1.25  # +25%目標
        
        risk = entry - stop
        reward = target - entry
        risk_reward = reward / risk if risk > 0 else 0
        
        if risk_reward < 3.0:
            return None
        
        # 結果を返す
        return {
            'ticker': ticker,
            'stage': 2,
            'rs_new_high': stage_result['details']['rs_new_high'],
            'has_vcp': True,
            'pivot': vcp_result['pivot'],
            'entry_price': entry,
            'stop_price': stop,
            'target_price': target,
            'risk_pct': risk_pct,
            'risk_reward': risk_reward,
            'current_price': data['close'].iloc[-1],
            'volume_50d_avg': data['volume_ma_50'].iloc[-1],
            'last_updated': data.index[-1].strftime('%Y-%m-%d')
        }
```

---

### 6. メインスクリプト（python/main.py）
```python
"""
メインスクリプト
"""
import yaml
import pandas as pd
from pathlib import Path
from loguru import logger

from screening.screener import Screener
from utils.logger import setup_logger

def load_config(config_path: str = "config/params.yaml") -> dict:
    """設定ファイル読み込み"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def load_tickers(tickers_path: str = "config/tickers.csv") -> list:
    """銘柄リスト読み込み"""
    df = pd.read_csv(tickers_path)
    return df['ticker'].tolist()

def main():
    """メイン処理"""
    # 設定読み込み
    config = load_config()
    
    # ログ設定
    setup_logger(
        log_path=config['output']['log_path'],
        log_level=config['output']['log_level']
    )
    
    logger.info("=" * 50)
    logger.info("Stock Screening Started")
    logger.info("=" * 50)
    
    # 銘柄リスト読み込み
    tickers = load_tickers()
    logger.info(f"Loaded {len(tickers)} tickers")
    
    # スクリーニング実行
    screener = Screener(config)
    results = screener.screen(tickers)
    
    if results.empty:
        logger.warning("No candidates found")
        return
    
    # 結果をソート（リスク・リワード比の高い順）
    results = results.sort_values('risk_reward', ascending=False)
    
    # CSV出力
    output_path = config['output']['csv_path']
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    
    logger.info(f"Results saved to: {output_path}")
    logger.info(f"Total candidates: {len(results)}")
    
    # サマリー表示
    print("\n" + "=" * 80)
    print("TOP 10 CANDIDATES")
    print("=" * 80)
    print(results.head(10).to_string(index=False))
    print("=" * 80)

if __name__ == "__main__":
    main()
```

---

### 7. ユーティリティ（python/utils/logger.py）
```python
"""
ログ設定モジュール
"""
from loguru import logger
from pathlib import Path
import sys

def setup_logger(log_path: str = "output/screening.log", log_level: str = "INFO"):
    """
    ロガーをセットアップ
    
    Args:
        log_path: ログファイルパス
        log_level: ログレベル
    """
    # 既存のハンドラーをクリア
    logger.remove()
    
    # コンソール出力
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    
    # ファイル出力
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_path,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        rotation="10 MB",
        retention="30 days"
    )
    
    return logger
```

---

## 実装順序

### Step 1: 基盤構築
```bash
cd C:\00_mycode\Invest\python

# ディレクトリ作成
mkdir data analysis screening backtest utils config output tests

# requirements.txt作成
# （上記の内容）

# インストール
pip install -r requirements.txt
```

### Step 2: 設定ファイル作成
1. `config/params.yaml` - 上記パラメータをコピー
2. `config/tickers.csv` - S&P 500銘柄リスト作成

### Step 3: データ取得実装
1. `data/fetcher.py` - yfinance実装
2. テスト: 1銘柄（AAPL）でデータ取得確認

### Step 4: テクニカル指標実装
1. `analysis/indicators.py` - 全指標実装
2. ユニットテスト作成

### Step 5: ステージ判定実装
1. `analysis/stage_detector.py` - Stage 2判定
2. テストケース作成

### Step 6: VCP検出実装
1. `analysis/vcp_detector.py` - VCP検出
2. テストケース作成

### Step 7: 統合
1. `screening/screener.py` - スクリーニング統合
2. `main.py` - メインスクリプト
3. CSV出力確認

### Step 8: バックテスト
1. `backtest/engine.py` - バックテスト実装
2. 2020-2025期間でテスト

---

## テスト方針

### ユニットテスト例
```python
# tests/test_indicators.py
import pytest
import pandas as pd
from analysis.indicators import calculate_sma

def test_calculate_sma():
    """SMA計算テスト"""
    data = pd.DataFrame({
        'close': [100, 102, 104, 106, 108, 110]
    })
    
    result = calculate_sma(data, [3])
    
    # 最後の3日平均
    expected = (106 + 108 + 110) / 3
    assert abs(result['sma_3'].iloc[-1] - expected) < 0.01
```

---

## 実行コマンド
```bash
# スクリーニング実行
cd C:\00_mycode\Invest\python
python main.py

# テスト実行
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ --cov=. --cov-report=html
```

---

## 出力フォーマット（CSV）
```csv
ticker,stage,rs_new_high,has_vcp,pivot,entry_price,stop_price,target_price,risk_pct,risk_reward,current_price,volume_50d_avg,last_updated
AAPL,2,TRUE,TRUE,187.50,189.38,182.30,236.72,0.037,6.69,185.20,85000000,2025-01-27
MSFT,2,TRUE,TRUE,378.50,382.19,368.00,477.74,0.037,6.74,375.80,22000000,2025-01-27
NVDA,2,TRUE,TRUE,495.80,500.76,485.50,625.95,0.030,8.20,492.10,45000000,2025-01-27
```

---

## トラブルシューティング

### yfinanceエラー対策
```python
# リトライロジック
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_with_retry(symbol, period):
    return yf.Ticker(symbol).history(period=period)
```

### レート制限対策
```python
# リクエスト間隔を調整
fetcher = YahooFinanceFetcher(request_delay=1.0)  # 1秒待機
```

---

## パフォーマンス最適化

### 並列処理（オプション）
```python
from concurrent.futures import ThreadPoolExecutor

def screen_parallel(self, tickers: List[str]) -> pd.DataFrame:
    """並列スクリーニング"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(self._process_ticker, ticker, benchmark_data)
            for ticker in tickers
        ]
        results = [f.result() for f in futures if f.result()]
    
    return pd.DataFrame(results)
```

---

## 成功基準

### Phase 1完了条件
- [ ] 1,500銘柄のスクリーニングが動作
- [ ] Stage 2候補が50-150銘柄抽出
- [ ] VCP候補が10-30銘柄検出
- [ ] CSV出力が正常
- [ ] 全ユニットテストパス
- [ ] 実行時間が60分以内

---

## 将来的なアップグレード

### データソース
- Polygon.io（$29/月〜）
- Alpha Vantage（無料枠あり）

### 機能追加
- リアルタイム監視
- LINE通知
- Electron UI統合
- バックテスト詳細分析
