# サイト全体の日本語化計画（最小実装）

更新日時: 2026-03-05

## 目的

- サイト全体（/home を含む全ページ）の静的表示文言を日本語化し、画面右上のトグルボタンで英語⇄日本語を切り替えられるようにする。最小実装で段階的に翻訳範囲を拡大する。

## Task3 STEP 1: PLAN（サイト全体 i18n）

### 変更箇所（予定）

- frontend/src/main.tsx
  - i18n 初期化読み込みを追加。
- frontend/src/i18n.ts（新規）
  - i18next/react-i18next の初期化設定（fallbackLng: en）。
- frontend/src/locales/en.json（新規または拡張）
- frontend/src/locales/ja.json（新規）
- frontend/src/App.tsx
  - 右上 Language Toggle（EN/JA）を全ページ共通で表示。
- frontend/src/pages/Home.tsx, frontend/src/pages/BacktestDashboard.tsx, 主要コンポーネント
  - 固定文言を `t('...')` に段階置換。
- frontend のテストファイル
  - 言語切替の表示確認テストを追加。

### 影響範囲

- 影響あり: frontend 全ページの表示文言。
- 影響なし: backend API、python ロジック。

### 受け入れ基準

- 右上トグルで EN/JA を切替できる。
- `/home` と `/dashboard` を含む主要画面で文言が切替される。
- `?lang=ja` 指定時に初期言語が日本語になる。
- 未翻訳キーは英語でフォールバックする。

### 参照アセット・参照 URL

- https://analytics.metaplanet.jp/?lang=ja&tab=charts
- https://metaplanet.jp/en

### STEP 3: REVIEW（Task3 実装後）

- 機能: 全ページ共通ナビゲーションに右上 EN/JA トグルを追加し、`/home`, `/`, `/dashboard`, `/chart/:ticker` の主要文言切替を確認。
- アクセシビリティ: トグルは button 要素で実装し、キーボード操作可能。
- パフォーマンス: i18n リソースはローカル JSON を同期ロードし、追加通信なしで切替可能。
- ライセンス: 翻訳追加のみで外部アセット追加なし。
- 検証:
  - `npm --prefix frontend run test`
  - `npm --prefix frontend run build`
  - `docs/PLAN/assets/i18n_home_ja_task3.png`

## 範囲

- 対象: frontend 側の静的テキスト（ページヘッダ、フッタ、Hero、カード、CTA 等）。
- 除外: 外部 API の返却文（動的コンテンツの自動翻訳は別フェーズ）、コンテンツ管理システム連携。

## 技術方針（推奨・最小実装）

1. i18n 基盤: react-i18next を導入して Provider をアプリルートに配置する。
2. 翻訳ファイル: frontend/src/locales/en.json（既存英語）および frontend/src/locales/ja.json（新規）を用意する。
3. 言語切替 UI: Header に LanguageToggle（"EN" / "JA"）を右上に追加し、クリックで localStorage に選択言語を保存、クエリパラメータ `?lang=ja` でも切替可能にする（最小実装はクエリパラメータ経由での再読み込みも許容）。
4. コンポーネント変更: 各ページ/コンポーネントの静的文言を直接埋め込まず、`t('key')` で参照するように段階的に差し替える。
5. フォールバック: 翻訳キー未登録時は英語を表示する（i18next の fallbackLng を利用）。

## 実装ステップ（短期・順序）

1. plan-sitewide-i18n-create: react-i18next の導入、Provider 設置、en.json/ja.json の雛形作成。
2. plan-sitewide-i18n-toggle: Header に LanguageToggle を実装し、選択を localStorage と query param で保持・反映する。
3. plan-sitewide-i18n-translate-core: 主要ページ（/home, /dashboard, 共通 Header/Footer）を翻訳キーに差し替える。
4. plan-sitewide-i18n-tests: vitest（ユニット）と Playwright（E2E）で言語切替と主要文言の表示を確認するテストを追加。
5. plan-sitewide-i18n-docs: docs/COMMAND.md にローカル確認手順（例: /home?lang=ja）を追記。

## テストと受け入れ基準

- 右上の LanguageToggle で英語⇄日本語の切替が可能であること（主要テキストが切替される）。
- クエリパラメータ `?lang=ja` を付けてページを開くと日本語表示になること。
- 翻訳未設定のキーがあってもページが壊れない（英語フォールバック）。
- レイアウトやアクセシビリティに影響を与えないこと。

## 変更ファイル（想定・最小）
- frontend/src/i18n.ts（i18next 初期化）
- frontend/src/locales/en.json（新規または拡張）
- frontend/src/locales/ja.json（新規翻訳ファイル）
- frontend/src/components/Header.{js,jsx,tsx}（LanguageToggle 実装）
- frontend/src/pages/*（主要ページの翻訳キー差し替え）
- tests/*（vitest/Playwright の簡易テスト）

## 運用上の注意

- 画像や外部文言は権利者確認が必要なものがあるため、翻訳対象から除外または別途運用ルールを設ける。
- 一度に全ファイルを差し替えるとリスクが高いため、重要ページから段階的に実施する。

---

備考: 最小実装ではクエリパラメータによる切替を採用し、将来的にユーザー設定として保存する拡張を行う。
