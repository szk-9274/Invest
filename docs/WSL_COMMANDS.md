# WSL: tmux と Copilot 起動メモ

以下は WSL 上でこのリポジトリを操作するための簡易メモです。ルートは /mnt/c/00_mycode/Invest を想定しています。

## tmux セッション作成
```bash
# 新しい tmux セッションを作る
tmux new -s ai
# 作業ディレクトリに移動
cd /mnt/c/00_mycode/Invest/Python
source .venv/bin/activate
```

## Copilot CLI（対話例）
```bash
# 単発実行
copilot --model gpt-5.3-codex --yolo


# 複数オプションで起動（autopilot など）
cd /mnt/c/00_mycode/Invest

copilot \
  --model gpt-5.3-codex \
  --yolo \
  --autopilot \
  --add-dir /mnt/c/00_mycode/Invest


copilot \
  --model gpt-5 mini \
  --yolo \
  --autopilot \
  --add-dir /mnt/c/00_mycode/Invest
```

## tmux のデタッチ/アタッチ
- デタッチ: Ctrl+B, D
- 再アタッチ: tmux attach -t ai

（必要ならこのセクションを docs/COMMAND.md に統合します）
