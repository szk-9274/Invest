## Claude Code Configuration

### 設定ファイル構成

```
.claude/
├── agents/                    # 👤 人格・役割分担（思考モード）
│   ├── planner.md             # 設計担当：実装前に計画を立てる
│   ├── tdd-guide.md           # テスト担当：TDD・最小再現テストを要求
│   └── code-reviewer.md       # レビュアー：品質・リスク・設計妥当性を確認
│
├── commands/                  # 🚀 起動装置（人が明示的に呼ぶワークフロー）
│   ├── plan.md                # /plan - 実装計画の作成
│   ├── tdd.md                 # /tdd - テスト駆動で修正・実装
│   ├── code-review.md         # /code-review - 変更差分のレビュー
│   └── build-fix.md           # /build-fix - ビルド／実行エラー修正
│
├── rules/                     # 📜 条例（分野別の詳細ルール）
│   ├── coding-style.md        # コーディング規約
│   ├── testing.md             # テスト必須条件・実行ルール
│   ├── git-workflow.md        # ブランチ戦略・PR運用
│   └── security.md            # セキュリティ・危険操作禁止
│
├── skills/                    # 🧠 技能（再利用可能な作業ノウハウ）
│   ├── tdd-workflow.md        # TDDの具体的手順
│   └── electron-patterns.md   # Electron実装パターン（※他PJ流用可）
│
├── rules.md                   # 🏛 憲法（最上位ルール・思想）
├── settings.json              # ⚙️ Claude Code 共通設定（共有）
└── settings.local.json        # 🔐 ローカル専用設定（個人環境）

```

### 使い方

1. **テスト駆動開発**: `/tdd` コマンドでTDDワークフローを開始
2. **実装計画**: `/plan` コマンドで計画を作成
3. **コードレビュー**: `/code-review` でコード品質をチェック
4. **ビルド修正**: `/build-fix` でビルドエラーを自動修正

### 設定元

設定は [everything-claude-code](https://github.com/affaan-m/everything-claude-code) をベースに、Electron + React + TypeScript プロジェクト用にカスタマイズしています。

---

### Next.js + React + TypeScript + Tailwind

Next.js: Reactを土台にしたフルスタックWebフレームワーク（ルーティング、SSR/SSG、APIなど）。サーバー側はNode.js/Edgeで動く
React: UIライブラリ。主にブラウザで動く（SSR等ではサーバーでも実行）
TypeScript: 型付きJavaScript。開発時に型チェック、ビルドでJavaScriptへトランスパイル
Tailwind CSS: ユーティリティファーストCSS。ビルド時に使ったクラスだけのCSSを生成、実行時はブラウザで適用
Node.js: 実行環境（エンジン）。開発・ビルド・SSRやAPIの土台。スタック表記では省略されがち

#### 備考
なぜ「Next.js + React + TypeScript + Tailwind」にNode.jsが載らないことが多いのか
実行環境（インフラ）だから: アプリの「中身（フレームワーク/ライブラリ）」ではなく「エンジン」

実行モデルのまとめ（どこで何が動くか）
中身（あなたが書くもの）: Next.js + React + TypeScript + Tailwind
エンジン（それを動かすもの）: Node.js（＋場合によりEdgeランタイム）
だから一覧にはNode.jsを書かないことが多いが、実運用では前提として必須になることが多い

---
#### install
Node.jsのインストール

https://nodejs.org にアクセス
“Current”（最新版、22系）Windows Installer (.msi) をダウンロード
インストーラで「Add to PATH」にチェックしたままインストール
PowerShellを開き、以下で確認
node -v → v22.x.x が表示されればOK
npm -v → npmのバージョンが出ればOK
```
任意のフォルダ作成
npm init -y

$env:HTTP_PROXY = "http://in-proxy-o.denso.co.jp:8080"
$env:HTTPS_PROXY = "http://in-proxy-o.denso.co.jp:8080"
$env:ELECTRON_GET_USE_PROXY="true"

npm config set proxy http://in-proxy-o.denso.co.jp:8080
npm config set https-proxy http://in-proxy-o.denso.co.jp:8080
```

必要パッケージの導入
```
npm i electron systeminformation execa --verbose

npm i -D electron-builder

npx electron --version
```
npx tsc --init をルートで実行

#### ico
プロジェクト直下に build フォルダを作る
正しい Windows 用アイコン build/icon.ico を用意
（256/128/64/48/32/16px を内包したICO）
```
winget install ImageMagick.ImageMagick
magick build\icon.png -define icon:auto-resize=256,128,64,48,32,16 -define icon:format=bmp build\icon.ico
package.json の build.win.icon を "build/icon.ico" に
```

VSCode 設定に追加（settings.json）
```
"css.lint.unknownAtRules": "ignore"
```
インストール（Tailwind v4）
```
npm i -D tailwindcss @tailwindcss/postcss postcss autoprefixer
```
---

#### Electron + Vite（React）開発

目標フォルダ構成（ソースのみ）
.
├── build/
│ ├── icon.ico
│ └── icon.png
├── renderer/
│ ├── index.html
│ ├── src/
│ │ ├── App.tsx
│ │ ├── main.tsx
│ │ ├── components/
│ │ ├── types/
│ │ └── index.css
│ └── tsconfig.json
├── src/
│ ├── main.ts
│ └── preload.ts
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── README.md

※ 生成物は .gitignore に含める: dist/, renderer-dist/, release/


起動コマンド
```
npm run tsc:watch
npm run renderer:dev
npm run electron:dev
```

製品版相当の確認（自動リロードはしません）
```
npm run start:prod
```
renderer-dist/ が生成される
```
npm run build
```
release削除
```
cmd /c rmdir /s /q release
```
release/ にインストーラー生成
```
npm run dist
```

---

## Stock Screening System (Minervini Stage Theory)

ミネルヴィニのステージ理論とVCPパターンに基づく株式スクリーニングシステム。

### Python環境セットアップ

```powershell
cd C:\00_mycode\Invest\python

# 仮想環境作成（初回のみ）
python -m venv venv
# 仮想環境起動
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

```

### テスト実行

```powershell
cd C:\00_mycode\Invest\python

# 全テスト実行
pytest

# 特定のテストファイル実行
pytest tests/test_ticker_fetcher_smoke.py -v

# カバレッジ付きで実行
pytest --cov=. --cov-report=html
```

**テストガイドライン**: 詳細は [docs/testing_guidelines.md](docs/testing_guidelines.md) を参照

**重要**: `scripts/` ディレクトリのコードを修正する場合は、必ず対応する smoke test を追加・更新してください。

### コマンド一覧

#### 1. 銘柄リストの更新（約3,500銘柄を取得）

```powershell
cd C:\00_mycode\Invest\python
python scripts/update_tickers_extended.py

# オプション指定
python scripts/update_tickers_extended.py --min-market-cap 5000000000 --max-tickers 2000
```

#### 2. Stage 2 スクリーニング（基本）

```powershell
# Stage 2銘柄のみを抽出
python main.py --mode stage2

# クイックテスト（5銘柄）
python main.py --mode test

# Stage 2 + VCPパターン（フル分析）
python main.py --mode full
```

#### 3. ファンダメンタルズ付きスクリーニング

```powershell
# Stage 2 + ファンダメンタルズフィルター（EPS成長率25%以上、売上成長率25%以上）
python main.py --mode stage2 --with-fundamentals
```

#### 4. バックテスト実行

```powershell
# デフォルト期間（2020-01-01 ~ 2025-01-27）
python main.py --mode backtest

# 期間指定
python main.py --mode backtest --start 2022-01-01 --end 2024-12-31

# 特定銘柄のみ
python main.py --mode backtest --tickers AAPL,MSFT,NVDA
```

### 出力ファイル

| ファイル | 説明 |
|---------|------|
| `output/screening_results.csv` | スクリーニング結果 |
| `output/screening.log` | 実行ログ |
| `output/backtest/trades.csv` | トレード詳細 |
| `output/backtest/equity_curve.png` | 資産曲線グラフ |
| `output/backtest/drawdown.png` | ドローダウングラフ |
| `output/backtest/monthly_returns.png` | 月次リターン表 |

### 設定ファイル

| ファイル | 説明 |
|---------|------|
| `config/params.yaml` | スクリーニング・バックテストパラメータ |
| `config/tickers.csv` | スクリーニング対象銘柄リスト |

### ファンダメンタルズフィルター条件（Minervini基準）

- EPS成長率: 前年同期比 +25%以上
- 売上高成長率: 前年同期比 +25%以上
- 四半期加速: QoQ（四半期対前期）で成長加速
- 営業利益率: 15%以上（オプション）

## Stage2 Filtering Modes (New!)

The system now supports **two filtering modes** to handle zero-trades scenarios:

### Strict Mode (Default)
- High-quality setups with tighter thresholds
- Best for bull markets with many candidates
- 9 Stage2 conditions all must pass

### Relaxed Mode (Automatic Fallback)
- Looser thresholds for harsh market conditions
- Automatically activates if strict mode produces 0 trades
- Increases trade opportunities while maintaining core trend structure

### Configuration

Edit `python/config/params.yaml`:

```yaml
stage:
  # STRICT MODE (default)
  strict:
    min_price_above_52w_low: 1.30      # 30% above 52-week low
    max_distance_from_52w_high: 0.75   # Within 25% of 52-week high
    rs_new_high_threshold: 0.95        # RS ≥ 95% of 52w high
    min_volume: 500000

  # RELAXED MODE (fallback)
  relaxed:
    min_price_above_52w_low: 1.20      # 20% above (easier)
    max_distance_from_52w_high: 0.60   # Within 40% of high (easier)
    rs_new_high_threshold: 0.90        # RS ≥ 90% (easier)
    min_volume: 300000

  # Fallback behavior
  auto_fallback_enabled: true          # Enable automatic fallback
  min_trades_threshold: 1              # Fallback if < 1 trade
```

**See [docs/STAGE2_TUNING_GUIDE.md](docs/STAGE2_TUNING_GUIDE.md) for detailed tuning instructions.**

## Manual Testing Commands

### Test Stage2 Filtering

```bash
# 1. Update ticker list (Stage1 filtering)
python scripts/update_tickers_extended.py

# 2. Run Stage2 screening
python main.py --mode stage2

# 3. Run backtest to verify trades are generated
python main.py --mode backtest --start 2023-01-01 --end 2024-01-01
```

### Debug Specific Ticker

To see why a specific ticker fails Stage2 conditions:

```bash
python scripts/debug_stage2.py AAPL
```

### Check Diagnostics

Backtest output shows:
- Filtering mode used (STRICT or RELAXED)
- Total Stage2 checks performed
- Pass/fail breakdown by condition
- Most common failure reasons

Example output:
```
BACKTEST CONFIGURATION
=========================
Filtering mode:   STRICT
Auto fallback:    Enabled

BACKTEST DIAGNOSTICS
=========================
Stage 2 checks performed:    8,450
Stage 2 passed:               156
Total trades executed:         12

Top Stage 2 failure reasons:
  near_52w_high            4,234 failures
  rs_new_high              2,891 failures
```

### Test Fallback Behavior

```bash
# Test on harsh market period (should trigger fallback)
python main.py --mode backtest --start 2022-01-01 --end 2022-12-31

# Look for "[FALLBACK]" messages in logs
```