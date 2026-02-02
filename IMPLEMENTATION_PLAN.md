# ティッカー情報取得パイプライン改善 - 実装計画

## 📋 プロジェクト概要

現在のティッカー情報取得パイプラインについて、信頼性・再実行性・API耐性・効率性を向上させる改善を実施する。

### 改善の目的
- Yahoo Finance APIの制限・BAN回避
- 長時間処理の中断耐性向上
- 失敗時の再実行コスト削減
- 重要銘柄の優先的取得保証

---

## 🎯 タスク一覧

### Task 1️⃣: 失敗ティッカーの永続化（CSV保存）
**優先度**: 🔴 HIGH
**依存関係**: なし
**推定工数**: 中（2-3時間）

#### 目的
- API失敗ティッカーを再実行時に活用
- 成功済みティッカーをスキップ可能にする

#### 実装チェックリスト
- [ ] 失敗ティッカーを `python/config/failed_tickers.csv` に保存
- [ ] 保存内容: ticker, error_type, timestamp, retry_count
- [ ] 再実行時に成功済みティッカーをスキップ
- [ ] CSVが存在しない場合でも安全に動作

#### テスト条件
- [ ] 意図的に失敗ティッカーを含めて実行
- [ ] CSVが生成されることを確認
- [ ] 再実行でスキップが効いていることを確認

#### 変更ファイル
```
python/scripts/update_tickers_extended.py  # 失敗記録/読込ロジック
python/tests/test_failed_ticker_persistence.py  # 新規テスト
```

---

### Task 2️⃣: クールダウン + 指数バックオフの導入
**優先度**: 🔴 HIGH
**依存関係**: なし
**推定工数**: 中（2-3時間）

#### 目的
- Yahoo APIのレート制限・BAN回避
- 連続失敗時の耐性向上

#### 実装チェックリスト
- [ ] 連続失敗回数をカウント
- [ ] 失敗回数に応じて待機時間を指数的に増加（5s → 10s → 20s → 40s...）
- [ ] 一定時間成功したらクールダウンをリセット
- [ ] ログにクールダウン理由と秒数を明示

#### テスト条件
- [ ] 疑似的に連続失敗を発生させる
- [ ] 待機時間が段階的に増えていることを確認

#### 変更ファイル
```
python/data/fetcher.py  # クールダウンロジック追加
python/scripts/update_tickers_extended.py  # 連続失敗カウント統合
python/tests/test_exponential_backoff.py  # 新規テスト
```

---

### Task 3️⃣: バッチ処理の安全性・再開性向上
**優先度**: 🟡 MEDIUM
**依存関係**: Task 1（失敗記録があると相乗効果）
**推定工数**: 中（2-3時間）

#### 目的
- 長時間処理の途中失敗でもやり直しコストを下げる

#### 実装チェックリスト
- [ ] バッチ単位で進捗を `python/config/batch_progress.json` に保存
- [ ] 中断後の再実行で完了済みバッチをスキップ
- [ ] 未処理分のみ続行
- [ ] 進捗ログを明確に出力

#### テスト条件
- [ ] 実行途中で意図的に中断
- [ ] 再実行で続きから始まることを確認

#### 変更ファイル
```
python/scripts/update_tickers_extended.py  # 進捗保存/読込ロジック
python/tests/test_batch_resumability.py  # 新規テスト
```

---

### Task 4️⃣: 取得結果のキャッシュ化（短期）
**優先度**: 🟢 LOW
**依存関係**: なし
**推定工数**: 小（1-2時間）

#### 目的
- 同一ティッカーへの不要な再リクエスト削減
- 再実行の高速化

#### 実装チェックリスト
- [ ] ティッカー情報をローカルキャッシュに保存（既存pickleキャッシュ活用）
- [ ] キャッシュ有効期限を24hに調整（現在12h）
- [ ] 有効なキャッシュがある場合はAPIを呼ばない
- [ ] キャッシュヒット / ミスをログ出力

#### テスト条件
- [ ] 同じ処理を連続実行
- [ ] 2回目以降でAPI呼び出しが減ることを確認

#### 変更ファイル
```
python/data/fetcher.py  # キャッシュTTL調整、ログ追加
python/tests/test_cache_mechanism.py  # 新規テスト
```

---

### Task 5️⃣: ティッカー取得優先順位の導入（時価総額順）
**優先度**: 🟡 MEDIUM
**依存関係**: Task 2（クールダウンがあると効果的）
**推定工数**: 中（2-3時間）

#### 目的
- 価値の高い銘柄を優先して確実に取得
- API制限にかかっても「重要銘柄が先に取れている」状態を作る

#### 実装チェックリスト
- [ ] ティッカーに優先度を付与（時価総額ベース）
- [ ] 優先度の基準: 時価総額が大きい銘柄を優先、不明な場合は後回し
- [ ] 処理順が優先度順になるよう制御
- [ ] ログで「優先処理中」であることが分かる表示

#### テスト条件
- [ ] 大型株が先に処理されていることをログで確認

#### 変更ファイル
```
python/scripts/update_tickers_extended.py  # 優先順ソート追加
python/tests/test_ticker_prioritization.py  # 新規テスト
```

---

## 🔧 アーキテクチャ影響分析

### 既存コードベースとの互換性
✅ **既存仕様を破壊しない設計**

1. **CSV出力形式**: `config/tickers.csv` の形式は変更しない
2. **API呼び出しインターフェース**: `fetcher.py` のメソッドシグネチャは維持
3. **フィルタリングロジック**: `params.yaml` の基準は変更しない
4. **ログ形式**: 既存ログと衝突しないプレフィックス使用

### 新規ファイル
```
python/config/
  ├── failed_tickers.csv        # Task 1: 失敗記録
  └── batch_progress.json       # Task 3: バッチ進捗

python/tests/
  ├── test_failed_ticker_persistence.py  # Task 1
  ├── test_exponential_backoff.py        # Task 2
  ├── test_batch_resumability.py         # Task 3
  ├── test_cache_mechanism.py            # Task 4
  └── test_ticker_prioritization.py      # Task 5
```

### 変更対象ファイル
```
python/data/fetcher.py                      # Task 2, 4
python/scripts/update_tickers_extended.py   # Task 1, 2, 3, 5
```

---

## 🧪 テスト戦略（TDD Required）

### テストピラミッド
```
        E2E Tests (1)
       /           \
  Integration (5)
 /                  \
Unit Tests (15-20)
```

### テスト種別

#### 1. Unit Tests（各タスクで3-4個）
- CSV読込/書込（Task 1）
- 指数バックオフ計算（Task 2）
- JSON進捗保存/復元（Task 3）
- キャッシュヒット判定（Task 4）
- 優先度ソート（Task 5）

#### 2. Integration Tests（各タスクで1個）
- 失敗ティッカーの再実行フロー（Task 1）
- クールダウン発動条件（Task 2）
- バッチ中断→再開（Task 3）
- キャッシュ有効期限管理（Task 4）
- 優先順処理の実行順（Task 5）

#### 3. E2E Test（全タスク完了後）
- 実際のYahoo Finance APIを使用
- 10ティッカー程度で全機能確認
- ログ出力の確認

### カバレッジ目標
- **最低**: 80%
- **目標**: 90%+

---

## 📊 実装順序（推奨）

### Phase 1: 基盤整備（最優先）
1. **Task 1**: 失敗ティッカーの永続化 → 再実行の効率化
2. **Task 4**: キャッシュ化（24h） → API負荷軽減

### Phase 2: 耐性向上
3. **Task 2**: 指数バックオフ → API BAN回避
4. **Task 3**: バッチ再開性 → 長時間処理の安定化

### Phase 3: 最適化
5. **Task 5**: 優先順位付け → 重要銘柄の確実取得

---

## ⚠️ リスク評価

### 🔴 HIGH Risk
1. **Yahoo Finance API制限**
   - リスク: 過度な並列処理でBAN
   - 対策: Task 2の指数バックオフ優先実装

2. **既存データ破損**
   - リスク: CSV/JSON書き込みエラーで既存データ消失
   - 対策: 書き込み前にバックアップ作成

### 🟡 MEDIUM Risk
3. **処理時間増加**
   - リスク: クールダウンで全体処理時間が2-3倍に
   - 対策: 許容範囲（仕様書で明記済み）

4. **ディスク容量**
   - リスク: キャッシュ/進捗ファイルの肥大化
   - 対策: 古いファイルの定期削除ロジック

### 🟢 LOW Risk
5. **テスト実行時間**
   - リスク: E2Eテストで実際のAPI呼び出し
   - 対策: モックを使用した高速テスト優先

---

## ✅ Definition of Done（完了条件）

### 各タスク
- [ ] チェックリスト項目がすべて完了
- [ ] テストカバレッジ80%以上
- [ ] 単体テスト・統合テストが全てパス
- [ ] ログ出力で動作確認可能
- [ ] コードレビュー完了（`/code-review`）

### プロジェクト全体
- [ ] Task 1〜5 がすべて実装済み
- [ ] 最低1回、実際にスクリプトを実行して成功
- [ ] 実行ログにより以下が確認できる:
  - スキップ（Task 1, 3）
  - クールダウン（Task 2）
  - 優先順（Task 5）
  - 再開性（Task 3）
  - キャッシュヒット（Task 4）
- [ ] すべてのテストがパス（65 existing + 15-20 new = 80-85 tests）
- [ ] ドキュメント更新（README, IMPLEMENTATION_SUMMARY.md）

---

## 📝 実装メモ

### コーディング規約
- **イミュータビリティ**: 常にオブジェクトのコピーを作成
- **ファイルサイズ**: 200-400行が標準、800行が最大
- **エラーハンドリング**: すべての外部I/Oで try-catch
- **型安全性**: TypeHintを積極使用

### ロギング規約
```python
# 既存ログとの衝突回避
logger.info("[CACHE HIT] Ticker: AAPL")  # Task 4
logger.warning("[COOLDOWN] Waiting 20s due to 5 consecutive failures")  # Task 2
logger.info("[PRIORITY] Processing mega-cap: AAPL ($3T)")  # Task 5
logger.info("[SKIP] Batch 3/10 already completed")  # Task 3
logger.error("[FAIL] Ticker: XYZ | Error: HTTPError")  # Task 1
```

### Git Commit規約
```bash
feat(persistence): add failed ticker CSV tracking
feat(backoff): implement exponential cooldown
feat(batch): add resumable batch processing
feat(cache): extend TTL to 24h with hit/miss logging
feat(priority): add market cap-based ticker prioritization
```

---

## 🚀 次のステップ

1. **Task 1から順番に実装開始**
2. **各タスクでTDDサイクルを遵守**
   - RED → GREEN → REFACTOR
3. **タスク完了ごとに `/code-review` 実行**
4. **全タスク完了後にE2Eテスト実行**
5. **ドキュメント更新とコミット**

---

## 📞 サポート

実装中の質問や問題は GitHub Issues へ報告してください。
