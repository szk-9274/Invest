# WSL: tmux と Copilot 起動メモ

以下は WSL 上でこのリポジトリを操作するための簡易メモです。ルートは $HOME/code/Invest を想定しています。

## tmux セッション作成
```
# 新しい tmux セッションを作る
tmux new -s ai
# 作業ディレクトリに移動
cd $HOME/code/Invest/python
source .venv/bin/activate
```

## Copilot CLI（対話例）


# 複数オプションで起動（autopilot など）
```
wsl
cd $HOME/code/Invest/python
source .venv/bin/activate
cd $HOME/code/Invest
./devinit.sh

copilot \
 --model gpt-5.3-codex \
 --autopilot \
 --yolo \
 --allow-all \
 --add-github-mcp-toolset all \
 --add-dir ~/code/Invest

copilot \
 --model gpt-5-mini \
 --autopilot \
 --yolo \
 --allow-all \
 --add-github-mcp-toolset all \
 --add-dir ~/code/Invest
```

## tmux のデタッチ/アタッチ
exit
wsl --shutdown
tmux kill-server
- デタッチ: Ctrl+B, D
- 再アタッチ: tmux attach -t invest

（必要ならこのセクションを docs/COMMAND.md に統合します）
