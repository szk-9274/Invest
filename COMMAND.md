# COMMAND.md
Invest プロジェクト — 実行コマンド集

このファイルは開発・検証で頻出するコマンドをプロジェクト標準に合わせてまとめたものです。古くなった手順や環境固有のメモは削除・統合しています。

---

## 1) 環境の一括起動（推奨）
リポジトリルートで tmux による開発環境を一括起動する場合:

just dev

- `just dev` は `./devinit.sh` を呼び出して tmux セッション（invest）を作成/再接続します。
- devinit.sh は backend / frontend / copilot / logs / git のペイン構成で起動します。lazygit を使用します。

補助:
just stop    # tmux セッションを停止
just logs    # tail -F backend.log frontend.log
just test    # python のテスト実行（python/.venv を利用）
just lint    # python lint（ruff）
just fmt     # python 格納の整形

---

## 2) バックエンド（API）
推奨: リポジトリルートから実行して import パスが自然になるようにする。

# 仮想環境をアクティブにしてから
cd python
source .venv/bin/activate

# リポジトリルートに戻る
cd ..
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

API: http://localhost:8000

---

## 3) フロントエンド（React）

cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000 --strictPort

アプリ: http://localhost:3000

ビルド/テスト:
npm run build
npm run test -- --testNamePattern TopBottomPurchaseCharts

---

## 4) Python 実行コマンド（ローカル CLI）
仮想環境を有効化して実行してください。

# 仮想環境作成/セットアップ
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 主なスクリプト
python main.py --mode backtest                    # デフォルトのバックテスト
python main.py --mode backtest --start 2023-01-01 --end 2023-12-31
python main.py --mode backtest --no-charts       # チャート生成をスキップ
python main.py --mode chart --ticker AAPL --start 2023-01-01 --end 2023-12-31
python scripts/update_tickers_extended.py --min-market-cap 5000000000

注意: 長時間実行するコマンドはジョブランナー（UI 経由）を使うことを推奨します。

---

## 5) ジョブ / API の確認 (curl)

curl http://localhost:8000/api/backtest/latest
curl http://localhost:8000/api/backtest/list
curl http://localhost:8000/health

ジョブ作成例（JSON body）:
curl -X POST http://localhost:8000/api/jobs -H "Content-Type: application/json" -d '{"command":"backtest","start_date":"2024-01-01","end_date":"2024-12-31"}'

---

## 6) デバッグ手順

- ブラウザで F12 を押し Console / Network を確認
- backend.log / frontend.log を tail -F で追う
- Python でのキャッシュクリア: rm -rf __pycache__ .pytest_cache
- Node のクリーンアップ: rm -rf node_modules && npm install

---

## 7) スクリーンショット取得（ローカル検証）
node scripts/capture-screenshot.js --url http://localhost:3000/dashboard --out tests/screenshots --sizes "1280x720,375x812"

（CI 用や headless 実行は環境依存。ローカルで動作することを確認してから CI に組み込んでください）

---

## 8) WSL / Windows 関連（統合）
WSL 環境から Windows 側にポートを転送する例（Windows 側で管理者権限 PowerShell 実行）:

# WSL 側で起動している Vite の 3000 ポートを Windows 側で公開する
# 例: netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=3000 connectaddress=<WSL_IP> connectport=3000

WSL での簡単なワークフロー:
cd $HOME/code/Invest
source python/.venv/bin/activate
./devinit.sh   # tmux ベースの開発環境を起動

tmux の基本:
- 新規作成: tmux new -s invest
- アタッチ: tmux attach -t invest
- デタッチ: Ctrl+B, D

---

## 9) Copilot / 自動作業ツールについて
Copilot CLI を使う場合は必ず必要な最小フラグのみを使い、権限や接続先を明示してください。プロジェクトの自動化用に特別なフラグや "--allow-all" のような非推奨/危険なオプションはドキュメントに残しません。使用例は管理者に確認の上実行してください。

---

## 10) 追加メモ
- テストは外部APIをモックしてください（CI の回帰テスト要件）
- チャート表示の検証はローカルで先に行ってください（ヘッドレスは環境依存のため安定化が要る）

---

(このファイルは docs/WSL_COMMANDS.md の内容を統合済みです)
