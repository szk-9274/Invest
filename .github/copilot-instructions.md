# .github/copilot-instructions.md — Copilot 用指示（日本語）

このファイルは GitHub Copilot / 自動化エージェントがこのリポジトリで安全かつ効果的に動作するための要点をまとめたものです。
主にビルド／テスト実行コマンド、アーキテクチャの要点、リポジトリ固有の規約を短く示します。

---

## 1) 主要なビルド・実行・テストコマンド（現状）

- Python (バックエンド / スクリプト)
  - 仮想環境有効化（Windows PowerShell）:
    ```powershell
    cd C:\00_mycode\Invest\python
    .\.venv\Scripts\Activate.ps1
    ```
  - FastAPI 開発サーバ:
    ```powershell
    cd C:\00_mycode\Invest\backend
    python -m uvicorn app:app --reload --port 8000
    ```
  - スクリプト実行（Stage2 / Backtest 等）:
    ```powershell
    cd C:\00_mycode\Invest\python
    python main.py --mode stage2
    python main.py --mode backtest --start 2023-01-01 --end 2024-01-01
    # チャート生成をスキップ: --no-charts
    ```
  - 単一スクリプト実行例:
    ```powershell
    python scripts/update_tickers_extended.py --min-market-cap 5000000000
    ```

- Frontend (React + TypeScript)
  - 開発サーバ (ホットリロード):
    ```powershell
    cd C:\00_mycode\Invest\frontend
    npm run dev
    # フロントは http://localhost:3000
    ```
  - ビルド（存在する場合）:
    ```powershell
    cd C:\00_mycode\Invest\frontend
    npm run build
    ```
  - Electron / デスクトップ関連 (root package.json にスクリプトあり):
    - 開発: `npm run dev:hmr` / `npm run electron:dev`
    - 製品相当確認: `npm run start:prod`
    - ビルド: `npm run build`, インストーラー: `npm run dist`

- テスト (主に Python)
  - 全テスト実行:
    ```powershell
    cd C:\00_mycode\Invest\python
    pytest
    ```
  - 単一テスト実行例:
    ```powershell
    pytest tests/test_ticker_fetcher_smoke.py -v
    ```
  - カバレッジ:
    ```powershell
    pytest --cov=. --cov-report=html
    ```

- 型チェック / リント
  - リント用の専用スクリプトは見つかりませんでした。TypeScript の型チェックは次で実行できます:
    ```powershell
    cd C:\00_mycode\Invest\frontend
    npx tsc --noEmit
    ```

---

## 2) 高レベルアーキテクチャ（要点）

- python/: バックテスト／スクリーニングの本体（CLI で実行、出力は CSV / PNG）。
- backend/: FastAPI サーバが python の出力ディレクトリを読み、JSON（チャートは base64 Data URI）で返す。
- frontend/: React + TypeScript による表示層（計算ロジックは禁止、API からの表示専用）。
- 出力パス例: `python/output/backtest/backtest_YYYY-MM-DD_to_YYYY-MM-DD_YYYYmmdd-HHMMSS/`（trades.csv, ticker_stats.csv, charts/*.png 等）。
- データフロー: python -> output files -> FastAPI -> フロントエンド（REACT_APP_API_URL で接続先を切替）。

---

## 3) リポジトリ固有の主要規約（Copilot が従うべき事項）

- TDD 優先: 新しいロジックや script 変更はまずテストを書く（RED→GREEN→REFACTOR）。
- テスト要件: 外部 API は必ずモック、ネットワーク禁止、テストは短時間で完了（目安: 5 秒以内）。
- 出力契約: CSV / DataFrame の必須カラム（例: `ticker, exchange, sector, stage`）は明示し、変更時は契約テストを追加。
- ステージ分離: Stage1 / Stage2 / Backtest は疎結合。下流は上流の出力のみ参照。
- ログ出力: `print()` 禁止。構造化ロガーを使用すること。
- DataFrame 安全チェック必須: `if df is None or df.empty: return` のようなガードを入れる。
- 機密情報: コードにハードコード禁止。環境変数を使う。
- 仕様更新: 戦略やスクリーニング条件を変える場合は必ず STRATEGY.md を更新し、PR に理由を明記。
- Git / PR: Conventional Commits、main 直push 禁止、PR はテスト通過必須。

---

## 4) API / 型・コンパチビリティに関する注意

- API は現状 JSON + charts: `data:image/png;base64,...` で返却される（フロントはこれをそのまま表示）。この交換形式を勝手に変更しないこと。変更する場合は backend の TypeScript 型定義と tests を同時に更新する。
- フロントは計算ロジックを持たない（表示専用）。重いロジックは python 側で実行させる。

---

## 5) Copilot への具体的な指示（行動方針）

- 設計を壊す変更をしない。大きな構造変更は計画 (plan) を立て、ユーザに確認する。
- 変更提案には必ず対応するテスト（ユニットまたはスモーク）を添付する。
- API 変更提案はバックエンドとフロント両方の型/実装差分を示すこと。
- 変更は小さく段階的に行い、ドキュメント（STRATEGY.md / COMMAND.md）を更新する。

---

## 6) 参照すべきファイル（起点）
- README.md
- COMMAND.md
- CONTRIBUTING.md
- STRATEGY.md
- python/、backend/、frontend/ ディレクトリ

---
