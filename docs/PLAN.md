# 開発計画

## 問題
開発端末外（スマホ等）から frontend / backend にアクセス可能にし、SSH 接続時に tmux の `invest` セッションへ自動復帰できるようにする。

## 実装アプローチ
既存の `devinit.sh` の pane 起動コマンドのみを最小差分で更新し、4ペイン構成（backend/frontend/copilot/logs）は維持する。加えて `~/.bashrc` の末尾に tmux 自動復帰設定を追記する。

## タスク
- [ ] `devinit.sh` の backend pane コマンドを `python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000` に変更する。
- [ ] `devinit.sh` の frontend pane コマンドを `npm run dev -- --host` に変更する。
- [ ] `devinit.sh` のレイアウト定義を確認し、`backend / frontend / copilot / logs` の4ペイン構成が維持されていることを確認する。
- [ ] `~/.bashrc` 末尾に tmux 自動復帰設定を追記する。
- [ ] 変更後ファイルを表示し、必要な確認結果を報告する。

## 影響範囲
- 変更ファイル: `devinit.sh`, `~/.bashrc`, `docs/PLAN.md`
- 実行時影響:
  - backend が `0.0.0.0:8000` で待ち受ける
  - frontend(Vite) が外部アクセス可能な host で待ち受ける
  - SSH ログイン時に tmux セッション `invest` へ自動 attach/new が実行される
