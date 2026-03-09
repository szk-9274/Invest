# COMMAND.md
Invest プロジェクト — 実行コマンド集

---

## 1) 環境の一括起動（推奨）
リポジトリルートで tmux による開発環境を一括起動する場合:

```
wsl
cd ~/code/Invest/python
source ./.venv/bin/activate
cd ~/code/Invest
just dev
```

```
# tmux の全セッションを終了（完全停止）
tmux kill-server
# 特定セッションだけ終了
tmux kill-session -t invest
# tmux のデタッチ
tmux detach
# tmux の全クライアントを強制デタッチ
tmux detach-client -a
# tmux 確認
tmux ls
```

- `just dev` は `./devinit.sh` を呼び出して tmux セッション（invest）を作成/再接続します。
- devinit.sh は backend / frontend / copilot / logs / git のペイン構成で起動します。lazygit を使用します。

---

## 2) バックエンド（API）
推奨: リポジトリルートから実行して import パスが自然になるようにする。

### 仮想環境をアクティブにしてからリポジトリルートに戻る
```
cd $HOME/code/Invest/Python
source python/.venv/bin/activate
cd $HOME/code/Invest/backend
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
API: http://localhost:8000
```

---

## 3) フロントエンド（React）
```
cd $HOME/code/Invest/Python
source python/.venv/bin/activate
cd $HOME/code/Invest/frontend

npm run dev -- --host 0.0.0.0 --port 3000 --strictPort

アプリ: http://localhost:3000

ビルド/テスト:
npm run build
npm run test -- --testNamePattern TopBottomPurchaseCharts
```

---

## 4) Python 実行コマンド（ローカル CLI）
仮想環境を有効化して実行してください。

### 仮想環境作成/セットアップ
```
# 初回のみ
cd $HOME/code/Invest/Python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 主なスクリプト
```
python main.py --mode backtest                    # デフォルトのバックテスト
python main.py --mode backtest --start 2023-01-01 --end 2023-12-31
python main.py --mode backtest --no-charts       # チャート生成をスキップ
python main.py --mode chart --ticker AAPL --start 2023-01-01 --end 2023-12-31
python scripts/update_tickers_extended.py --min-market-cap 5000000000
```

