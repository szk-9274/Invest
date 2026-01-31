## Claude Code Configuration

このプロジェクトには Claude Code の設定が含まれています。

### 設定ファイル構成

```
.claude/
├── agents/                    # サブエージェント
│   ├── tdd-guide.md           # TDD専門（テストファースト）
│   ├── code-reviewer.md       # コードレビュー
│   └── planner.md             # 実装計画作成
│
├── commands/                  # スラッシュコマンド
│   ├── tdd.md                 # /tdd - テスト駆動開発
│   ├── plan.md                # /plan - 実装計画
│   ├── code-review.md         # /code-review - コードレビュー
│   └── build-fix.md           # /build-fix - ビルドエラー修正
│
├── rules/                     # 常に従うルール
│   ├── security.md            # Electronセキュリティ
│   ├── coding-style.md        # コーディングスタイル
│   ├── testing.md             # テスト要件
│   └── git-workflow.md        # Gitワークフロー
│
└── skills/                    # ワークフロー定義
    ├── electron-patterns.md   # Electronパターン
    └── tdd-workflow.md        # TDDワークフロー
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

```
tsc:watch（main/preloadを監視）
renderer:dev（Vite dev server）
electron:dev（dist を nodemon 監視し、Electron を再起動。USE_DEV_SERVER=true で dev server を表示）
```
```
npm run tsc:watch
npm run renderer:dev
npm run electron:dev
```

まとめてやりたい場合は「npm run dev:hmr」（tsc:watch + renderer:dev + electron:dev を並列起動）でもOKです
```
npm run dev:hmr
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

## 開発環境セットアップ履歴（2026-01-22）

### インストール・修正内容

#### 1. 依存関係のインストール
```bash
npm install
```
全ての依存パッケージがインストールされます。

#### 2. Electronバージョンの変更
`package.json` の Electron バージョンを `31.x` に変更しました。
```json
"electron": "^31.7.7"
```
※ 環境依存の問題を回避するため安定版を使用

#### 3. electron-launcher.js の追加
`ELECTRON_RUN_AS_NODE` 環境変数が設定されている環境（VSCode拡張、Claude Code等）でも
Electronが正常に起動するためのラッパースクリプトを追加しました。

```javascript
// electron-launcher.js
// ELECTRON_RUN_AS_NODE 環境変数をクリアしてからElectronを起動
```

#### 4. package.json スクリプトの修正
`electron:dev` スクリプトを修正し、`electron-launcher.js` を使用するようにしました。

```json
"electron:dev": "wait-on -v dist/main.js tcp:127.0.0.1:5173 && cross-env USE_DEV_SERVER=true nodemon --watch dist --ext js --exec \"node electron-launcher.js .\""
```

### 注意事項
- `ELECTRON_RUN_AS_NODE=1` が設定された環境では、Electronが Node.js モードで動作し、
  Electron API (app, ipcMain, BrowserWindow等) が利用できなくなります。
- `electron-launcher.js` はこの問題を回避するために環境変数を削除してからElectronを起動します。

---

## Stock Screening System (Minervini Stage Theory)

ミネルヴィニのステージ理論とVCPパターンに基づく株式スクリーニングシステム。

### Python環境セットアップ

```powershell
cd C:\00_mycode\Invest\python

# 仮想環境作成（初回のみ）
python -m venv venv
.\venv\Scripts\Activate.ps1

# 依存パッケージインストール
pip install yfinance pandas numpy loguru tqdm pyyaml tenacity matplotlib
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