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