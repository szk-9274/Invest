# 実装計画: リポジトリ名を MinerviLism へ統一

- フェーズ: リポジトリ識別子更新
- プラン: `FPXszk` / `MinerviLism` への統一漏れを解消し、localhost で backend 結果が取得できない不具合を修正する
- 責任者: Copilot
- 目的: リポジトリ全体を探索して旧 GitHub ユーザー名 `szk-9274` と旧リポジトリ名 `Invest` の残存参照を修正し、localhost 開発時に frontend / Electron から backend のバックテスト結果を取得できない原因を TDD で潰し、関連ドキュメント・設定・テストを整合させる
- 前提:
  - GitHub アカウントのユーザーネーム変更後、`origin` remote は `git@github.com:FPXszk/MinerviLism.git` へ更新済み
  - ローカル作業ディレクトリは `~/code/MinerviLism` へ移行済み
  - 旧識別子の残りはコード・ドキュメント・テスト・補助スクリプト・生成物に点在している可能性がある
- 進捗: planning

## 変更・削除・作成するファイル
- 更新候補: `README.md`, `ARCHITECTURE.md`, `COMMAND.md`
- 更新候補: `docs/design-docs/localhost-visualization-improvements.md`, `docs/product-specs/index.md`, `docs/generated/doc-inventory.md`
- 更新候補: `tests/test_experiment_manifest.py`, `backend/tests/**/*`, `frontend/src/api/*.test.ts`
- 更新候補: `frontend/src/api/base.ts`, `frontend/vite.config.ts`, `frontend/src/**/*`
- 更新候補: `backend/api/backtest.py`, `backend/services/result_store.py`, `backend/services/result_loader.py`
- 更新候補: `.github/workflows/playwright-screenshots.yml`, `scripts/capture-screenshot.js`, `scripts/mock-backend.js`
- 再生成候補: `renderer-dist/**/*` など build 生成物

## 実装内容
- リポジトリ全体を探索し、`szk-9274` と `Invest` の残存参照を洗い出す
- ソースコード・テスト・ドキュメント・workflow・補助スクリプトに残る旧識別子を `FPXszk` / `MinerviLism` に更新する
- 生成物に含まれる旧識別子は手編集せず、必要なら対応する build / generate コマンドで再生成する
- localhost で backend 結果が取得できない症状を再現し、API ベース URL / Vite proxy / backend の結果探索のどこで壊れているかを特定する
- 先に失敗するテストを追加または更新し、最小限の修正で GREEN にし、その後に関連ロジックを整理する
- 変更後に frontend / backend / docs の主要検証を実行し、結果取得と名称統一の回帰を確認する

## 影響範囲
- clone / remote / README に記載された識別子、URL、パス表記
- localhost 開発時の frontend API 呼び出し先と proxy 設定
- backend の `python/output/backtest` 探索と結果選択ロジック
- Playwright / mock backend / CI スクリプトの localhost 前提
- テスト fixture と assertion に埋め込まれた旧識別子

## 実装ステップ
- [ ] Task 1: baseline を取得する（旧識別子の残存箇所一覧、`git status`、関連設定、localhost 結果取得不具合の再現）
- [ ] Task 2: 旧 GitHub ユーザー名 `szk-9274` と旧リポジトリ名 `Invest` の残存参照を、ソース・テスト・ドキュメント・スクリプト単位で分類する
- [ ] Task 3: localhost 結果取得不具合に対する失敗テストを追加または更新し、原因を固定化する（RED）
- [ ] Task 4: 旧識別子の修正と localhost 結果取得ロジックの最小修正を実装し、失敗テストを通す（GREEN）
- [ ] Task 5: 関連コードを整理し、不要な重複や生成物の更新漏れを解消する（REFACTOR）
- [ ] Task 6: `bash tests/devinit_test.sh`、`./python/.venv/bin/python3 -m pytest backend/tests -q`、`npm --prefix frontend run test:coverage`、`npm run build`、`./python/.venv/bin/python3 scripts/doc_gardening.py`、`./python/.venv/bin/python3 scripts/check_docs.py` を実行して検証する
- [ ] Task 7: 差分をレビューし、計画を `docs/exec-plans/completed/` へ移す準備をしたうえでユーザー確認を待つ

## 注意点
- `renderer-dist` など生成物は直接編集せず、原因修正後に build で再生成する
- `docs/generated/doc-inventory.md` や exec-plan index は手編集せず、`./python/.venv/bin/python3 scripts/doc_gardening.py` で同期する
- localhost 不具合は frontend 側 URL 解決だけでなく backend 側の run 探索失敗も候補なので、症状を再現してから修正する
- 既存の unrelated change は触らず、今回のスコープに直結する箇所だけを更新する
