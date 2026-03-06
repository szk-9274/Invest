# iPhone表示最適化計画（/home と共通ナビ）

更新日時: 2026-03-07

## 計画レビュー結果（問題点）

旧版の `plan-iphone-display.md` はアセット収集メモ中心で、以下の問題がありました。

1. iPhone 向け実装対象（どのコンポーネントをどう直すか）が曖昧。
2. 既に完了済みの項目（`/home` ルーティング追加など）が残っており、現行コードとの差分が不明確。
3. STEP 2 / 4 / 5 / 6 の実行要件（実装・コミット分割・PR 記載・改善提案）が不足。
4. ライセンス参照ファイルの現在位置が反映されていない（`assets-licenses.md` は `docs/PLAN/_old/` 側）。

本ドキュメントは上記を修正した最新版です。

## STEP 1: PLAN

### 目的

- iPhone 幅（主に 390px 前後）で共通ナビゲーションが使いづらくなる問題を解消し、`/home` の表示導線を崩さずに操作性を改善する。

### 変更箇所（予定）

- `frontend/src/App.tsx`
  - 共通ナビにモバイルメニューの開閉 UI（ボタン）を追加。
  - モバイル環境でリンク群と言語トグルを折りたたみ表示できるようにする。
- `frontend/src/App.css`
  - iPhone 幅向けブレークポイント（<= 480px）でナビレイアウトを2段化し、横はみ出しを防止。
  - 既存デスクトップ表示を維持。
- `frontend/src/App.i18n.test.tsx`
  - 既存言語切替テストに加え、モバイルメニュー開閉と導線のテストを追加。
- `docs/PLAN/plan-iphone-display.md`
  - 実施結果（STEP 3 レビュー）を追記。

### 影響範囲

- 影響あり: frontend 全ページ共通のヘッダーナビ表示（`/`, `/home`, `/dashboard`, `/chart/:ticker`）。
- 影響なし: backend API、python の Stage1 / Stage2 / Backtest ロジック、出力契約。

### 受け入れ基準

1. iPhone 幅でナビが横スクロールせず、メニュー操作で各リンクに到達できる。
2. EN/JA 切替はモバイル表示でも機能する。
3. 既存ルーティング（`/home`, `/dashboard` など）とデスクトップ表示を壊さない。
4. `npm --prefix frontend run test -- --run` と `npm --prefix frontend run build` が成功する。

### 参照アセット・参照資料

- `docs/PLAN/assets/home_task2.png`（/home の参照スクリーンショット）
- `docs/PLAN/assets/i18n_home_ja_task3.png`（JA 表示参照）
- `docs/PLAN/_old/assets-licenses.md`（アセットライセンス管理）

## STEP 2: IMPLEMENT（予定）

1. 先にテスト（モバイルメニュー開閉）を追加して RED を確認。
2. `App.tsx` / `App.css` に最小差分でモバイルメニュー実装。
3. テストを GREEN にし、既存言語切替も回帰確認。

## STEP 3: REVIEW（実装後）

- 機能:
  - `App` の共通ナビにモバイルメニュー開閉ボタンを追加し、リンククリック時に確実に閉じる挙動を実装。
  - `App.i18n.test.tsx` にモバイルメニューの開閉と遷移時クローズのテストを追加し、RED -> GREEN を確認。
- アクセシビリティ:
  - メニューボタンに `aria-label` / `aria-expanded` / `aria-controls` を設定。
  - iPhone幅ではリンクと言語トグルを縦積み表示にし、タップしやすい領域を維持。
- パフォーマンス:
  - 追加は軽量な React state + CSS のみで、新規依存や重い処理は追加していない。
  - 既存のビルドサイズ傾向（Plotlyチャンク警告）は既知で、本対応では増加を最小限に抑制。
- ライセンス:
  - 新規アセット追加なし。既存資料参照のみで、外部ライセンスの新規リスクは増やしていない。
- 検証結果:
  - `npm --prefix frontend run test -- src/App.i18n.test.tsx --run` : PASS
  - `npm --prefix frontend run test -- --run` : PASS（66 tests）
  - `npm --prefix frontend run build` : PASS

## STEP 4: COMMIT（予定）

- コミットは機能単位で分割:
  - `docs:` PLANレビュー修正
  - `feat:` iPhoneナビ実装 + テスト

## STEP 5: PUSH（予定）

- feature ブランチを push し、PR を作成。
- PR には変更点・参照ファイル・スクリーンショットパスを記載。

## STEP 6: IMPROVEMENT（予定）

- PR コメントに改善案（コード品質/性能/テスト）を記載。
- 次タスクを `todos` に登録してから `ask_user` で次作業確認する。
