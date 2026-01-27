# ミネルヴィニ流 成長株投資 完全トレードルール

本ドキュメントは、マーク・ミネルヴィニのステージ理論、VCP（Volatility Contraction Pattern）、SEPA戦略に基づく厳格なロング専用トレードルールを定義します。

---

## 目次

1. [ステージ理論の定義](#1-ステージ理論の定義)
2. [各ステージの詳細](#2-各ステージの詳細)
3. [トレンドテンプレート（Stage 2判定条件）](#3-トレンドテンプレートstage-2判定条件)
4. [VCP（ボラティリティ収縮パターン）](#4-vcpボラティリティ収縮パターン)
5. [エントリールール](#5-エントリールール)
6. [リスク管理](#6-リスク管理)
7. [ポジションサイズ計算](#7-ポジションサイズ計算)
8. [利益確定（エグジット戦略）](#8-利益確定エグジット戦略)
9. [損切り・撤退ルール](#9-損切り撤退ルール)
10. [市場環境フィルター](#10-市場環境フィルター)
11. [実装用パラメータ定義](#11-実装用パラメータ定義)
12. [コード実装フロー](#12-コード実装フロー)

---

## 1. ステージ理論の定義

### 概要
ステージ理論（Stage Analysis）は、株価の長期トレンドを4つの状態に分類し、**第2ステージ以外では一切リスクを取らない**ための市場認識フレームワークである。

### 本質
> **「大きく勝てるのは、構造的な上昇トレンドに入った銘柄だけ」**

この事実を、感情ではなく**客観的な数値条件**で判定する。

---

## 2. 各ステージの詳細

### ステージ1：ベース形成期（Base）

**定義**
- 下落トレンドが止まり、横ばいでエネルギーを溜めている段階
- まだ上昇トレンドとは言えない

**特徴**
- 200日移動平均線（MA）が横ばい
- 株価は200日MA付近を上下
- 出来高は低調
- 強気材料と弱気材料が混在

**投資判断**
- ❌ **買わない**
- 理由：上にも下にも行き得る「未確定ゾーン」

---

### ステージ2：上昇期（Advancing）★唯一の買いゾーン

**定義**
- 機関投資家の資金流入により、持続的な上昇トレンドが確立した状態

**客観的条件（トレンドテンプレート）**
1. 株価 > 150日MA > 200日MA
2. 200日MAが明確な上昇トレンド（最低20営業日以上）
3. 52週高値の25%以内（Close ≥ High_52w × 0.75）
4. 52週安値から30%以上上昇（Close ≥ Low_52w × 1.30）
5. 50日MAが150日・200日MAの上
6. RS（相対力）70以上（理想は80〜90）
7. 平均出来高が十分（50万株/日以上）

**投資判断**
- ✅ **唯一「買ってよい」ステージ**
- 全リスクはこのステージに集中させる

---

### ステージ3：天井形成期（Topping）

**定義**
- 上昇トレンドが鈍化し、分配（Distribution）が始まる段階

**特徴**
- 200日MAが横ばい化
- 高値更新できなくなる
- 出来高を伴う乱高下
- 機関投資家の静かな売り抜け

**投資判断**
- ❌ **新規エントリー禁止**
- 保有中なら警戒モード

---

### ステージ4：下落期（Declining）

**定義**
- 明確な下落トレンドに入った状態

**特徴**
- 株価 < 200日MA
- 200日MAが下向き
- デッドクロス頻発
- 出来高を伴う急落

**投資判断**
- ❌ **絶対に買わない**
- ❌ **「安値拾い」は禁止**
- 速やかに撤退

---

## 3. トレンドテンプレート（Stage 2判定条件）

### 数値定義
```python
# 必須条件（全て満たす必要あり）
def is_stage2(data: pd.DataFrame, rs_line: pd.Series) -> bool:
    """
    Stage 2判定
    
    Args:
        data: 株価データ（OHLCV + 各種MA）
        rs_line: 相対力指標
    
    Returns:
        True: Stage 2条件を全て満たす
        False: 条件を満たさない
    """
    
    conditions = {
        # 1. 価格とMAの位置関係
        'price_above_ma': Close[t] > SMA_50[t] > SMA_150[t] > SMA_200[t],
        
        # 2. 200日MAの傾き（上昇トレンド）
        'ma200_uptrend': (SMA_200[t] - SMA_200[t-20]) > 0,
        
        # 3. 52週安値からの上昇
        'above_52w_low': Close[t] >= Low_52w[t] * 1.30,
        
        # 4. 52週高値への接近
        'near_52w_high': Close[t] >= High_52w[t] * 0.75,
        
        # 5. 50日MAの位置
        'ma50_position': (SMA_50[t] > SMA_150[t]) and (SMA_50[t] > SMA_200[t]),
        
        # 6. 相対力（RS）
        'rs_strength': (RS_Line[t] >= 52週高値) or (RS_Rating >= 70),
        
        # 7. 流動性
        'liquidity': AvgVol_50[t] >= 500_000
    }
    
    return all(conditions.values())
```

### パラメータ

| 項目 | 変数名 | 値 |
|------|--------|-----|
| 52週安値からの上昇率 | `min_price_above_52w_low` | 1.30（30%以上） |
| 52週高値への距離 | `max_distance_from_52w_high` | 0.75（25%以内） |
| 200日MA上昇期間 | `min_slope_200_days` | 20営業日以上 |
| RS最低レーティング | `rs_min_rating` | 70以上 |
| 最低平均出来高 | `min_volume` | 500,000株/日 |

---

## 4. VCP（ボラティリティ収縮パターン）

### 定義
VCPは、株価の変動率が段階的に収縮し、機関投資家の蓄積（Accumulation）が完了した状態を示すパターン。

### 検出条件

#### 4.1 ベース期間
- 期間：35〜65営業日
- 形状：横ばいまたは緩やかな上昇

#### 4.2 収縮シーケンス
連続する押し（Pullback）の幅が逓減する：
```
理想的なシーケンス例：
1回目の押し：25%
2回目の押し：15%
3回目の押し：8%
4回目の押し：5%以下
```

**条件**
- 最低3回以上の収縮
- 各収縮率が前回より小さい
- 最後の収縮は10%以下

#### 4.3 ドライアップ（出来高枯渇）
```python
# ドライアップ判定
dryup_confirmed = (AvgVol_10[t] / AvgVol_50[t]) <= 0.6
```

最後の収縮区間で：
- 10日平均出来高 ≤ 50日平均 × 0.6
- ATR（Average True Range）の低下

#### 4.4 ピボット（Pivot）
- 定義：ベース最上部の水平高値
- 条件：ピボット ≥ 52週高値 × 0.95（上値供給が軽微）

#### 4.5 ワイド&ルース回避
- ベース内の日次変動率の標準偏差が過去90日平均の1.2倍超なら不合格

---

## 5. エントリールール

### 5.1 事前条件
1. ✅ Stage 2条件を全て満たす
2. ✅ VCP品質合格
3. ✅ 市場環境良好（後述）
4. ✅ ピボット価格が定義済み

### 5.2 標準ブレイクアウトエントリー

#### トリガー条件（いずれか）
```python
# 条件1: 終値ベース
entry_trigger_1 = (
    Close[t] >= Pivot and
    Volume[t] >= AvgVol_50[t] * 1.5
)

# 条件2: 場中ブレイク
entry_trigger_2 = (
    High[t] >= Pivot and
    Close[t] >= Pivot and
    Volume[t] >= AvgVol_50[t] * 1.5
)
```

#### 買いゾーン
```python
# エントリー価格の許容範囲
buy_zone = Pivot * (1 + 0.03)  # ピボット+3%以内
entry_valid = Entry <= buy_zone
```

#### 失敗検出（フェイルドブレイク）
```python
# ブレイク後3営業日以内の失敗判定
failed_breakout = (
    Close[t] < Pivot and
    Volume[t] >= AvgVol_50[t] * 1.2 and
    days_since_breakout <= 3
)

if failed_breakout:
    # 全ポジション即座に撤退
    exit_all()
```

### 5.3 早期（チート）エントリー（任意）
```python
# ベース内の下降トレンドライン上抜け
# または直近10日高値更新

cheat_entry = (
    breakout_from_trendline or
    Close[t] > max(High[-10:])
) and Volume[t] >= AvgVol_50[t] * 1.2
```

**注意**：ストップはよりタイト（リスク増）

---

## 6. リスク管理

### 6.1 損失制限の数学的根拠

| 損失率 | 回復に必要な上昇率 |
|--------|-------------------|
| 10% | 11.1% |
| 20% | 25% |
| 33% | 50% |
| 50% | **100%** |

**結論**：50%の損失を出せば、元の資本に戻すだけで100%のリターンが必要。

### 6.2 損失上限
```python
# 1トレードあたりの損失制限
MAX_LOSS_PER_TRADE = 0.10  # 10%（絶対上限）
TARGET_AVG_LOSS = 0.05     # 5-6%（理想的平均）
```

### 6.3 初期ストップ計算
```python
def calculate_initial_stop(pivot: float, last_contraction_low: float, atr14: float) -> float:
    """
    初期ストップ価格を計算
    
    Args:
        pivot: ピボット価格
        last_contraction_low: 最後の収縮時の安値
        atr14: 14日ATR
    
    Returns:
        ストップ価格
    """
    # 候補1: ピボット-3%
    stop1 = pivot * 0.97
    
    # 候補2: 最後の収縮安値 - ATRバッファ
    stop2 = last_contraction_low - (0.5 * atr14)
    
    # より高い方を採用（リスクが小さい方）
    stop_price = max(stop1, stop2)
    
    return stop_price
```

### 6.4 ストップ検証
```python
def validate_stop(entry: float, stop: float) -> bool:
    """
    ストップが許容範囲内か検証
    
    Args:
        entry: エントリー価格
        stop: ストップ価格
    
    Returns:
        True: 許容範囲内
        False: リスク過大（見送り）
    """
    stop_distance_pct = (entry - stop) / entry
    
    # 条件
    valid = (
        stop_distance_pct <= 0.07 and  # 7%以内
        stop_distance_pct <= 0.10      # 絶対上限10%
    )
    
    return valid
```

### 6.5 リスク・リワード比
```python
# 最低リスク・リワード比
MIN_RISK_REWARD_RATIO = 3.0

# 検証
risk = entry - stop
expected_reward = target_price - entry
risk_reward = expected_reward / risk

if risk_reward < MIN_RISK_REWARD_RATIO:
    # トレード見送り
    pass
```

---

## 7. ポジションサイズ計算

### 7.1 基本公式
```python
def calculate_position_size(
    account_equity: float,
    entry: float,
    stop: float,
    risk_per_trade: float = 0.0075  # 0.75%
) -> int:
    """
    ポジションサイズを計算
    
    Args:
        account_equity: 口座残高
        entry: エントリー価格
        stop: ストップ価格
        risk_per_trade: 1トレードあたりのリスク（資産の%）
    
    Returns:
        購入株数
    """
    # 許容損失額
    allowed_loss = account_equity * risk_per_trade
    
    # 1株あたりの損失
    loss_per_share = entry - stop
    
    # 購入株数
    shares = int(allowed_loss / loss_per_share)
    
    return shares
```

### 7.2 例
```python
account_equity = 1_000_000  # 100万円
entry = 100.0               # エントリー: 100円
stop = 93.0                 # ストップ: 93円
risk_per_trade = 0.0075     # 0.75%

shares = calculate_position_size(account_equity, entry, stop, risk_per_trade)
# shares = 1071株

# 確認
total_investment = shares * entry  # 107,100円
max_loss = shares * (entry - stop) # 7,497円（資産の0.75%）
```

### 7.3 ナンピン禁止
```python
# ❌ 損失が出ている時の追加購入は禁止
# ✅ 含み益時のみ、追加セットアップで増し玉可能

if current_position_pnl < 0:
    # 追加購入禁止
    return False

# 増し玉は1回につきリスクの半分まで
add_shares = calculate_position_size(
    account_equity, 
    new_entry, 
    new_stop, 
    risk_per_trade * 0.5  # 半分
)
```

---

## 8. 利益確定（エグジット戦略）

### 8.1 初動管理（ブレイク後30日以内）
```python
# 条件1: 21日EMA割れ + 出来高増加
if Close[t] < EMA_21[t] and Volume[t] >= AvgVol_50[t] * 1.2:
    sell_percent(50)  # 50%利確

# 条件2: ボリンジャーバンド上限タッチ
if Close[t] >= BB_Upper20_2[t]:
    sell_percent(25)  # 25%利確
```

### 8.2 トレンド成熟管理
```python
# 強制全撤退: 50日MA割れ
if Close[t] <= SMA_50[t]:
    exit_all()  # 100%売却
    # これが最も重要なエグジット条件
```

### 8.3 段階利食い（任意）
```python
# +20〜25%到達
if (Close[t] - entry) / entry >= 0.20:
    sell_percent(33)  # 1/3利確
    # 残りは50日MA割れまで保有
```

### 8.4 過熱警戒
```python
# 3連続大陽線 + 高出来高
consecutive_big_days = all([
    (Close[t-i] - Close[t-i-1]) / Close[t-i-1] >= 0.03
    for i in range(3)
])

high_volume = Volume[t] >= AvgVol_50[t] * 1.5

if consecutive_big_days and high_volume:
    sell_percent(25)  # 25%利確
```

---

## 9. 損切り・撤退ルール

### 9.1 初期ストップ（必須）
```python
# エントリー時に設定したストップに到達
if Close[t] <= stop_price:
    exit_all()  # 即座に全撤退
    # 解釈・期待・希望は一切禁止
```

### 9.2 フェイルドブレイク
```python
# ブレイク後3日以内にピボット割れ + 出来高増加
if (
    days_since_breakout <= 3 and
    Close[t] < pivot and
    Volume[t] >= AvgVol_50[t] * 1.2
):
    exit_all()
```

### 9.3 異常陰線
```python
# 大陰線 + 高出来高
down_range = (Close[t] - Open[t]) / Open[t]

if (
    down_range <= -0.02 and  # -2%以上の陰線
    Volume[t] >= AvgVol_50[t] * 1.5
):
    exit_all()
```

### 9.4 ギャップダウン
```python
# 大きなギャップダウン
gap_down = (Open[t] - Close[t-1]) / Close[t-1]

if (
    gap_down <= -0.03 and  # -3%以上のギャップ
    Close[t] < pivot
):
    exit_all()
```

---

## 10. 市場環境フィルター

### 10.1 主要指数チェック
```python
def check_market_environment(index_data: pd.DataFrame) -> bool:
    """
    市場環境が良好か判定
    
    Args:
        index_data: S&P500等の指数データ
    
    Returns:
        True: エントリー可能
        False: 新規エントリー禁止
    """
    # 条件1: 指数がMA上
    above_ma = (
        index_data['Close'] > index_data['SMA_50'] and
        index_data['Close'] > index_data['SMA_200']
    )
    
    # 条件2: ディストリビューションデー
    dist_days = count_distribution_days(index_data, lookback=25)
    low_distribution = dist_days <= 5
    
    return above_ma and low_distribution

def count_distribution_days(data: pd.DataFrame, lookback: int = 25) -> int:
    """
    ディストリビューションデー（分配日）をカウント
    
    条件:
    - 終値が前日比-0.2%以上下落
    - 出来高が前日より増加
    """
    count = 0
    for i in range(lookback):
        down_day = (data['Close'].iloc[-i] - data['Close'].iloc[-i-1]) / data['Close'].iloc[-i-1] <= -0.002
        volume_up = data['Volume'].iloc[-i] > data['Volume'].iloc[-i-1]
        
        if down_day and volume_up:
            count += 1
    
    return count
```

### 10.2 エントリー制限
```python
# 市場環境が悪い場合
if not check_market_environment(spy_data):
    # 新規エントリー禁止
    allow_new_entries = False
    
    # 既存ポジションは50%に縮小を推奨
    reduce_positions_by(0.5)
```

### 10.3 決算イベント
```python
# 決算発表前後3日間
if days_to_earnings <= 3:
    # 新規エントリー禁止
    allow_new_entries = False
    
    # 既存ポジションは50%に縮小
    reduce_position_by(0.5)
```

---

## 11. 実装用パラメータ定義

### 11.1 変数定義
```python
from dataclasses import dataclass
from typing import List

@dataclass
class TradingParameters:
    """トレードパラメータ"""
    
    # ステージ判定
    sma_periods: List[int] = (50, 150, 200)
    min_price_above_52w_low: float = 1.30
    max_distance_from_52w_high: float = 0.75
    min_slope_200_days: int = 20
    rs_min_rating: int = 70
    min_volume: int = 500_000
    
    # VCP検出
    base_period_min: int = 35
    base_period_max: int = 65
    contraction_sequence: List[float] = (0.25, 0.15, 0.08, 0.05)
    last_contraction_max: float = 0.10
    dryup_vol_ratio: float = 0.6
    breakout_vol_ratio: float = 1.5
    pivot_min_high_52w_ratio: float = 0.95
    
    # エントリー
    buy_zone_pct: float = 0.03
    
    # リスク管理
    risk_per_trade: float = 0.0075
    max_loss_hard: float = 0.10
    initial_stop_max: float = 0.07
    pivot_buffer_atr: float = 0.5
    
    # エグジット
    partial_sell_bb_ratio: float = 0.25
    sma_50_exit: bool = True
    
    # 市場環境
    index_dist_days_max: int = 5
    earnings_window: int = 3
```

---

## 12. コード実装フロー

### 12.1 スクリーニングフロー
```python
def screen_stocks(tickers: List[str], params: TradingParameters) -> pd.DataFrame:
    """
    全銘柄をスクリーニング
    
    1. データ取得
    2. テクニカル指標計算
    3. ステージ判定
    4. VCP検出
    5. エントリー・ストップ計算
    6. リスク・リワード評価
    """
    results = []
    
    for ticker in tickers:
        try:
            # 1. データ取得
            data = fetch_data(ticker)
            benchmark = fetch_data('SPY')
            
            # 2. 指標計算
            data = calculate_indicators(data, params)
            rs_line = calculate_rs_line(data, benchmark)
            
            # 3. ステージ判定
            stage = detect_stage(data, rs_line, params)
            if stage != 2:
                continue
            
            # 4. VCP検出
            vcp = detect_vcp(data, params)
            if not vcp:
                continue
            
            # 5. エントリー・ストップ
            entry = vcp['entry_price']
            stop = vcp['stop_price']
            
            # 6. リスク検証
            risk_pct = (entry - stop) / entry
            if risk_pct > params.initial_stop_max:
                continue
            
            # 7. リスク・リワード計算
            target = entry * 1.25  # +25%目標
            risk_reward = (target - entry) / (entry - stop)
            
            if risk_reward >= 3.0:
                results.append({
                    'ticker': ticker,
                    'entry': entry,
                    'stop': stop,
                    'target': target,
                    'risk_reward': risk_reward,
                    'pivot': vcp['pivot']
                })
                
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
            continue
    
    return pd.DataFrame(results)
```

### 12.2 トレード実行フロー
```python
def execute_trade(ticker: str, signal: Dict, account: Account, params: TradingParameters):
    """
    トレード実行
    
    1. 市場環境確認
    2. ポジションサイズ計算
    3. エントリー注文
    4. ストップ設定
    5. エグジット監視
    """
    # 1. 市場環境
    if not check_market_environment():
        return "Market environment unfavorable"
    
    # 2. ポジションサイズ
    shares = calculate_position_size(
        account.equity,
        signal['entry'],
        signal['stop'],
        params.risk_per_trade
    )
    
    # 3. エントリー
    order = place_order(ticker, shares, signal['entry'])
    
    # 4. ストップ設定
    set_stop_loss(ticker, shares, signal['stop'])
    
    # 5. エグジット監視（別プロセス）
    monitor_exit(ticker, shares, signal)
```

---

## 黄金律（まとめ）

1. **資本保護はコストではなく、利益の源泉である**
2. **第2ステージ以外では取引しない**
3. **買う前に出口を決める**
4. **小さく負けて、大きく勝つ**
5. **規律を守った自分を評価せよ**

---

## 参考文献

- Mark Minervini, "Trade Like a Stock Market Wizard"
- Mark Minervini, "Think & Trade Like a Champion"
- Stan Weinstein, "Secrets for Profiting in Bull and Bear Markets"

---

## 改訂履歴

- 2025-01-27: 初版作成（完全実装仕様版）