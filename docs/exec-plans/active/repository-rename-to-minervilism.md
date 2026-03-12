# 実装計画: リポジトリ名を MinerviLism へ統一

- フェーズ: リポジトリ識別子更新
- プラン: GitHub / ローカル / ドキュメントの名称・所有者表記を `FPXszk` / `MinerviLism` に統一する
- 責任者: Copilot
- 目的: GitHub 上のリポジトリ名変更、SSH remote 更新、ローカルディレクトリ名変更、`devinit.sh` のルート修正、全リポジトリ探索による参照修正、検証、レビュー、push、改善提案 issue 追記までを安全に進める
- 前提:
  - GitHub アカウントのユーザーネームは `FPXszk` へ変更済み
  - `git config --global user.name "FPXszk"` は設定済み
  - GitHub 側プロフィール・アカウント ID は更新済み
- 進捗: planning

## 変更・削除・作成するファイル
- 更新候補: `devinit.sh`
- 更新候補: `README.md`, `COMMAND.md`, `ARCHITECTURE.md`
- 更新候補: `docs/**/*.md`, `.github/workflows/*.yml`, `tests/**/*`, `scripts/**/*`
- 更新候補: `package.json`, `docker-compose.yml`, `electron-launcher.js`, `frontend/**/*`, `backend/**/*`, `python/**/*`
- 更新候補: Git 設定 (`origin` remote)
- 外部変更: GitHub repository 名 (`Invest` -> `MinerviLism`)
- ローカル変更: ディレクトリ名 (`~/code/Invest` -> `~/code/MinerviLism`)

## 実装内容
- `gh` CLI を使って GitHub リポジトリ名を `Invest` から `MinerviLism` に変更する
- `origin` remote を `git@github.com:FPXszk/MinerviLism.git` に更新する
- ローカルディレクトリを `~/code/MinerviLism` にリネームし、以後は新パスで作業を継続する
- `devinit.sh` の `ROOT_DIR` と関連する固定パス/表示名を更新する
- リポジトリ全体を探索し、`szk-9274` と `Invest` に依存する箇所を洗い出して修正する
- 生成物/索引は手編集せず、必要に応じて `python scripts/doc_gardening.py` で再生成する
- 変更後にテスト・ビルド・ドキュメント整合性・`devinit.sh` 関連検証を実施する
- `git status` を確認し、変更レビュー後に push 可否をユーザーへ確認する
- push 後、既存 issue を確認し、改善提案を追記する

## 影響範囲
- GitHub repository URL と clone / remote 導線
- 開発手順ドキュメントに含まれるパス、URL、所有者名
- `devinit.sh` と tmux 起動導線
- GitHub Actions / スクリプト / テスト内のリポジトリ識別子参照
- ローカル作業パスに依存するコマンド例

## 実装ステップ
- [ ] Task 1: 現状確認と baseline を取得する（`git status`、remote、主要検証コマンドの可否確認）
- [ ] Task 2: `gh` CLI で GitHub repository 名を変更し、SSH remote を新 URL に更新する
- [ ] Task 3: ローカルディレクトリを `~/code/MinerviLism` に変更し、`devinit.sh` の `ROOT_DIR` を修正する
- [ ] Task 4: リポジトリ全体を探索して `szk-9274` / `Invest` 参照を修正し、必要なドキュメント・設定・テストを更新する
- [ ] Task 5: `bash tests/devinit_test.sh`、`pytest backend/tests -q`、`npm --prefix frontend run test:coverage`、`npm run build`、`python scripts/doc_gardening.py`、`python scripts/check_docs.py` を実行して影響を検証する
- [ ] Task 6: `git status` と差分レビューを行い、push してよいかをユーザーへ確認する
- [ ] Task 7: 承認後に push し、既存 issue に改善提案を追記する

## 注意点
- ディレクトリ rename 後は作業ルートが変わるため、以降のすべてのコマンド実行パスを新パスへ切り替える
- `docs/generated/doc-inventory.md` や exec-plan index は手編集せず、ドキュメント整備コマンドで同期する
- GitHub rename と remote 更新の順序を誤ると push / pull が失敗するため、外部変更の成功確認後に local 設定を更新する
- 既存の issue 追記は新規作成ではなく、内容が近い既存 issue を特定してコメントまたは本文追記で対応する
