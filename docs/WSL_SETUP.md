# WSL 用互換性チェック手順

このファイルは、WSL (Ubuntu など) 上で本プロジェクトを動かす際に互換性で注意すべき点と、実行して確認するコマンド群をまとめたものです。

## 目的
- WSL にインストールされたツールやライブラリが、プロジェクトの要件と乖離していないかをチェックする。
- 必要なシステムライブラリが不足している場合に備え、手順を提示する。

## まずやってほしいチェック（WSLで実行）
```bash
# 作業ディレクトリ
cd /mnt/c/00_mycode/Invest

# 環境情報の自動収集スクリプト（./scripts/wsl_env_check.sh を作成済）を実行
bash ./scripts/wsl_env_check.sh

# 直接確認したいコマンド
python3 --version
python3 -m pip --version
python3 -m pip freeze | sed -n '1,200p'
node --version
npm --version
npm ls --depth=0
```

## システム依存が疑われる主な Python パッケージ
- lxml: libxml2-dev / libxslt1-dev が必要
- mplfinance / matplotlib（コメントアウト済の場合は不要）: libfreetype6-dev / libpng-dev が必要な場合あり
- uvicorn[standard]: extras に依存するネイティブ拡張があるためビルドツールや互換性に注意

### apt で入れておくと良いもの（Ubuntu系）
```bash
sudo apt update && sudo apt install -y \
  build-essential python3-dev python3-venv libxml2-dev libxslt1-dev pkg-config libfreetype6-dev libpng-dev libssl-dev \
  dos2unix jq ripgrep fd-find tree tmux htop ncdu unzip zip
```

## Node / npm 側の注意点
- Electron を WSL 上で動かす場合は X11/Wayland 環境やディスプレイ転送が必要になるため別途検討が必要。
- Node の推奨バージョンはプロジェクトに明示されていませんが、devDependencies の一部は最新の Node を想定するため v18 以上を推奨します。
- 非対話シェル（`bash -lc`）でも nvm の Node を使えるように、`~/.profile` 側で nvm を読み込んでおくことを推奨します。

## 差分解消の実行コマンド（WSL）
```bash
cd /mnt/c/00_mycode/Invest

# Node 依存をクリーン再構築（ルート + frontend）
rm -rf node_modules frontend/node_modules
npm ci
cd frontend && npm ci && cd ..

# Python 依存を再構築
cd python
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
cd ..

# 最終レポート再生成
source python/.venv/bin/activate
bash ./scripts/wsl_env_check.sh
```

## 最終チェック
```bash
python3 --version
node --version
npm --version
python3 -m pip check
npm ls --depth=0
cd frontend && npm ls --depth=0 && cd ..
```

