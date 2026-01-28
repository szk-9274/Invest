以下の問題を同時に修正してください。既存設計を尊重し、最小限の変更で対応してください。
修正中は agent に含まれる code-review / test / refactor エージェントを適宜使用してください。

==================================================
【問題①】yfinance の DeprecationWarning を黙らせたい
==================================================

以下の警告が大量に出力され、ログが読みにくくなっています。

DeprecationWarning:
'Ticker.earnings' is deprecated as not available via API.
Look for "Net Income" in Ticker.income_stmt.

・挙動自体は問題ないため、warnings フィルタで警告を抑制したい
・UserWarning や他の重要な Warning は抑制しない
・DeprecationWarning のみ対象とする

対応方針：
- main.py の冒頭、もしくは fundamentals 処理に入る直前で
  warnings.filterwarnings を使って DeprecationWarning を無効化する
- yfinance 由来の DeprecationWarning のみ抑制すること

==================================================
【問題②】backtest 実行時の tz-aware / tz-naive エラー修正
==================================================

以下のエラーで backtest が停止します。

TypeError:
Invalid comparison between dtype=datetime64[ns, America/New_York] and Timestamp

原因：
- yfinance が返す benchmark_data.index が tz-aware (America/New_York)
- start_date / end_date が tz-naive
- pandas が比較を拒否している

修正方針：
- backtest 内で比較する日時は tz-naive に統一する
- benchmark_data が存在する場合のみ index の tz を安全に除去する
- SPY 無効 (--no-benchmark) 時の挙動は変更しない

想定修正箇所：
- backtest/engine.py
- benchmark_data をスライスする直前

例：
- benchmark_data.index.tz が not None の場合、tz_localize(None) を適用
- start / end も tz-naive に正規化

==================================================
【制約】
==================================================

- 既存 CLI オプションや挙動を変更しない
- --use-benchmark / --no-benchmark の意味を変えない
- ロジック変更は行わず、型・警告・互換性問題のみ修正する

==================================================
【完了条件】
==================================================

- python main.py --mode stage2 --with-fundamentals が警告なしで完走する
- python main.py --mode backtest が例外なく完走する
- 既存テストはすべて通過する
- 追加・修正した内容が分かるように commit を分ける

==================================================
【作業管理】
==================================================

以下のチェックボックス形式でタスクを分割し、完了次第チェックしてください。

- [ ] DeprecationWarning 抑制の実装
- [ ] tz-aware / tz-naive 問題の修正
- [ ] 影響範囲のコードレビュー
- [ ] backtest / stage2 の再実行確認
- [ ] テスト実行・確認
- [ ] マージリクエストの作成

すべて完了したら、マージリクエストを提出してください。
