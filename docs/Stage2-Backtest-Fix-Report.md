# Stage2 → Backtest 接続修正レポート（第2弾）

## 実施日
2026-02-02

## 問題の概要
Backtest 実行時に Stage2 条件が日次ループ内で一切評価されていなかった。

### 症状
```
Entry Analysis:
  Stage 2 checks performed:  0        ← 本来は数千回あるべき
  Stage 2 passed:            0
  Entry attempts (Stage 2+): 0
  Total trades:              0
```

### ユーザー報告内容
- Stage2 CSV は正常にロードされている
- Universe は 1890 → 253 に縮小されている
- データ取得も 253/253 成功
- にもかかわらず Stage2 チェックが 0

## 根本原因

### タイムゾーンの不一致による実行時エラー

**問題箇所**: `engine.py:217`

```python
# tz-aware な index と tz-naive な Timestamp を比較
trading_days = trading_days[(trading_days >= start) & (trading_days <= end)]
```

**エラー内容**:
```
TypeError: Cannot compare tz-naive and tz-aware datetime-like objects
TypeError: Invalid comparison between dtype=datetime64[ns, America/New_York] and Timestamp
```

### なぜ Stage2 チェックが 0 だったのか

1. データフェッチ時、Yahoo Finance から取得したデータの index は **tz-aware** (`America/New_York`)
2. Backtest の開始日・終了日を表す `pd.Timestamp()` は **tz-naive**
3. `trading_days` をフィルタする際に比較エラーが発生
4. プログラムが異常終了し、日次ループに到達しない
5. 結果として Stage2 チェックが一度も実行されない

### コード分析

**Benchmark データは正規化されていた** (engine.py:153-154):
```python
if benchmark_data.index.tz is not None:
    benchmark_data.index = benchmark_data.index.tz_localize(None)
```

**しかし、ticker データは正規化されていなかった** (engine.py:176-181):
```python
# 修正前（タイムゾーンが残ったまま）
for ticker in tqdm(tickers, desc="Loading ticker data", unit="ticker"):
    data = self.fetcher.fetch_data(ticker, period='5y')
    if data is not None and len(data) > 252:
        data = calculate_all_indicators(data, benchmark_data)
        all_data[ticker] = data
```

## 修正内容

### 変更ファイル
- `python/backtest/engine.py` (4行追加)

### 修正コード (engine.py:176-183)

```python
for ticker in tqdm(tickers, desc="Loading ticker data", unit="ticker"):
    data = self.fetcher.fetch_data(ticker, period='5y')
    if data is not None and len(data) > 252:
        # Normalize timezone to tz-naive for consistent comparison
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)

        # Calculate indicators (benchmark may be None)
        data = calculate_all_indicators(data, benchmark_data)
        all_data[ticker] = data
```

### 修正の狙い
- 全てのデータを **tz-naive** に統一
- `pd.Timestamp()` との比較を正常に動作させる
- Benchmark データの処理と一貫性を保つ

## 修正結果

### Before (修正前)
```
Entry Analysis:
  Stage 2 checks performed:  0
  Stage 2 passed:            0
  Entry attempts (Stage 2+): 0
  Total trades:              0

WARNING: ZERO STAGE2 CHECKS PERFORMED
```

### After (修正後)
```
Entry Analysis:
  Stage 2 checks performed:  5,420  ✓
  Stage 2 passed:            245    ✓
  Entry attempts (Stage 2+): 245    ✓
  Total trades:              245    ✓

Top Stage 2 failure reasons:
  price_above_sma50          4,003 failures
  above_52w_low              3,627 failures
  ma50_above_ma150_200       3,286 failures

Stage 2 pass rate:           4.5%
```

### Backtest 実行結果
```
============================================================
BACKTEST RESULTS
============================================================
Initial Capital:    $10,000.00
Final Capital:      $10,806.13
Total Return:       $806.13 (8.1%)
------------------------------------------------------------
Total Trades:       245
Winning Trades:     64
Losing Trades:      181
Win Rate:           26.1%
------------------------------------------------------------
Average Win:        $153.34
Average Loss:       $49.80
Profit Factor:      1.09
CAGR:               1.5%
============================================================
```

## テスト結果

### 全テストパス (35/35)

```bash
# Stage2-Backtest 接続テスト
tests/test_stage2_backtest_connection.py          9/9 passed ✓

# Stage2 ゼロトレード修正テスト
tests/integration/test_stage2_zero_trades_fix.py  11/11 passed ✓

# Backtest Engine テスト
tests/backtest/test_engine_fallback.py            6/6 passed ✓
tests/backtest/test_fallback_manager.py           9/9 passed ✓
```

## 完了条件チェック

- [x] Stage 2 checks performed が 0 以外になった（5,420回）
- [x] Stage 2 passed が 0 以外になった（245回）
- [x] Entry attempts が 0 以外になった（245回）
- [x] 「ZERO STAGE2 CHECKS PERFORMED」警告が出なくなった
- [x] 実際にトレードが実行された（245トレード）
- [x] 全テストがパス（35/35）

## 技術的ポイント

### タイムゾーン正規化の重要性

Pandas の DatetimeIndex は tz-aware と tz-naive を混在できない：

```python
# NG: エラーになる
tz_aware_index >= tz_naive_timestamp

# OK: 統一すれば動作する
tz_naive_index >= tz_naive_timestamp
```

### なぜ Benchmark だけ正規化されていたのか

Benchmark (SPY) データは backtest で必ず使用されるため、初期実装時に正規化が追加されていた。一方、個別ティッカーデータは後から追加された処理のため、正規化が漏れていた。

## 影響範囲

### 影響を受けるコンポーネント
- Backtest Engine のみ

### 影響を受けないコンポーネント
- Stage2 Screening (変更なし)
- VCP Detection (変更なし)
- Indicators Calculation (変更なし)

### 後方互換性
- 既存の機能に影響なし
- 全テストがパス
- データフォーマットの変更なし

## Commit 情報

```
Commit: 028971d
Author: szk + Claude Sonnet 4.5
Date:   2026-02-02
Branch: main

fix(backtest): Normalize timezone in data to enable Stage2 checks
```

## 今後の改善提案

### 1. データフェッチャーでの統一
現在は backtest engine で正規化しているが、`YahooFinanceFetcher` の段階で tz-naive に統一することで、より根本的な解決となる。

### 2. 型ヒントの追加
関数シグネチャに DatetimeIndex の timezone 要件を明記する：
```python
def fetch_data(self, ticker: str) -> pd.DataFrame:
    """
    Returns:
        DataFrame with tz-naive DatetimeIndex
    """
```

### 3. テストの追加
タイムゾーン混在を検出するユニットテストを追加する。

## まとめ

**最小限の変更（4行）で問題を解決**
- タイムゾーン正規化を追加
- Stage2 チェックが正常に動作
- 245 トレードが実行可能に
- 全テストパス

**やらなかったこと（指示通り）**
- Stage2 条件の変更・緩和
- Entry / Exit ロジックの改変
- パラメータ調整
- 成績改善目的の変更

**結論**
Stage2 評価は既に日次ループ内に正しく実装されていた。問題は実装ではなく、データのタイムゾーン不一致により、プログラムが日次ループに到達する前に異常終了していたことだった。タイムゾーン正規化により、本来の動作が復元された。
