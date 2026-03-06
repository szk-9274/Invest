# 開発計画（WSLネイティブ移行）

## 問題
開発リポジトリが `/mnt/c/00_mycode/Invest`（Windows filesystem）上にあり、WSL Git/ツール利用時に改行・パーミッション・パス依存の問題を誘発しやすい。  
これを `/home/FPXszk/code/Invest`（WSL Linux filesystem）へ移行し、WSLネイティブ開発に統一する。

## 実装アプローチ
1. リポジトリを WSL 側へ安全コピー（履歴保持）。
2. WSL Git の user/core 設定を確認・不足のみ設定。
3. Git 状態診断（status/remote/branch/log、差分有無）を実施。
4. リポジトリ全体を静的スキャンして Windows 依存（パス・コマンド）を抽出。
5. Python/Node/npm/vite/uvicorn/scripts の実行可能性を確認し、WSL向け修正案を整理。

## タスク
- [ ] `/home/FPXszk/code` を作成し、`/mnt/c/00_mycode/Invest` を `/home/FPXszk/code/Invest` へコピーする。
- [ ] 移行先で `git --version`、`git config --global user.name/email` を確認し、未設定時のみ設定する。
- [ ] `git config --global core.autocrlf input` と `git config --global core.filemode false` を適用・再確認する。
- [ ] 移行先で `git status` / `git remote -v` / `git branch` / `git log -5` を確認する。
- [ ] 改行起因差分判定（`git diff`、`git ls-files --eol`）を確認する。
- [ ] `backend` / `frontend` / `python` / `scripts` / `docs` を対象に Windows パス依存・Windows コマンド依存をスキャンする。
- [ ] Python / Node / npm / vite / uvicorn / scripts のWSL適合性を診断し、必要な修正案を提示する。
- [ ] 最終レポートとして、原因・再発防止設定・安全な運用手順・推奨ディレクトリ構造をまとめる。

## 影響範囲
- 変更ファイル:
  - `docs/PLAN.md`（本計画）
  - （必要時のみ）WSL対応のためのドキュメント/スクリプト更新
- 実行時影響:
  - 開発作業ディレクトリが `/home/FPXszk/code/Invest` に移る
  - Git 改行変換・fileMode 差分の発生確率を低減
  - Windows 固有パス/コマンドの残存箇所を可視化できる

## devinit.sh 起動不具合修正計画（2026-03-06）

### 問題
- `./devinit.sh` 実行時、既存 tmux セッション `invest` が不完全でも再利用され、4ペイン起動コマンドが流れない。
- その結果、「スマホ表示向けモード」表示後に backend/frontend/copilot/logs の起動確認ができない状態になる。

### タスク
- [ ] `devinit.sh` に既存セッションの健全性チェック（4ペイン構成確認）を追加する。
- [ ] 不完全セッションを自動で再作成し、4ペインへ起動コマンドを再投入する。
- [ ] 既存正常セッション再利用時の挙動（attachのみ）を維持する。
- [ ] 手動検証で「壊れた既存セッション」および「新規起動」を確認する。

### 影響範囲
- 変更ファイル: `devinit.sh`
- 実行時影響: tmux セッション再利用ロジックのみ（戦略/バックテストロジックへの影響なし）

## devinit.sh 改善計画（2026-03-06 all）

### タスク
- [ ] `devinit.sh` に `--reset` オプションを追加する（既存セッション強制再作成）。
- [ ] 起動前に tmux セッション健全性サマリ（pane count/title）を表示する。
- [ ] `tests/devinit_test.sh` を新規追加し、tmux モックで主要分岐を検証する。
- [ ] `docs/COMMAND.md` に `./devinit.sh --reset` とテスト実行手順を追記する。

### 影響範囲
- 変更ファイル: `devinit.sh`, `tests/devinit_test.sh`, `docs/COMMAND.md`
- 非影響: Stage1/Stage2/Backtest の売買ロジック、API 契約

## logs ペイン backend/frontend 同時表示 修正計画（2026-03-06）

### 問題
- `devinit.sh` の logs ペインは `backend.log` のみを追尾しており、`frontend.log` が表示されない。
- backend/frontend の起動出力がログファイルへ確実に蓄積される前提が弱く、logs ペインで両方の進行状況を確認しづらい。

### タスク
- [ ] `tests/devinit_test.sh` を追加し、logs ペインの追尾対象が `backend.log` と `frontend.log` の両方であることを RED で確認する。
- [ ] `devinit.sh` に `FRONTEND_LOG_FILE` を追加し、backend/frontend 起動コマンドの出力をそれぞれ `tee -a` でログ保存する。
- [ ] logs ペインのコマンドを `backend.log` と `frontend.log` の同時追尾に修正する（`tail -F`）。
- [ ] `docs/COMMAND.md` に devinit 利用時の logs ペイン確認観点（2ファイル同時追尾）を追記する。
- [ ] テスト実行で GREEN を確認し、既存挙動を壊していないことを検証する。

### 影響範囲
- 変更ファイル: `devinit.sh`, `tests/devinit_test.sh`（新規）, `docs/COMMAND.md`
- 非影響: Stage1/Stage2/Backtest ロジック、バックエンド API 契約、フロント表示ロジック
