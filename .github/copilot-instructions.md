# Copilot Instructions

このファイルは、このリポジトリで作業する AI の行動ルールを定義します。

---
## 行動ルール
- ユーザーとは日本語でコミュニケーションを取ること。思考の過程も日本語で表現すること。
- /home/fpxszk/code/Invest をルートフォルダとして作業する。
- データパイプライン設計（Stage1 / Stage2 / Backtest）を崩さない。  
- ステージ間は疎結合を維持し、下流は上流の出力のみを参照する。  
- 再現性・決定性を最優先し、未来データ参照（look-ahead）を禁止する。  
- ロジック変更は TDD（RED -> GREEN -> REFACTOR）で進める。  
- テストでは外部 API をモックし、ネットワーク依存を持ち込まない。  
- `python/scripts/` の変更時は CLI 引数検証・Fail Fast・スモークテストを重視する。  
- `print()` は使わず、既存の logger を使う。  
- DataFrame を扱う処理は `None` / `empty` ガードを入れる。  
- 機密情報はハードコードせず、環境変数で扱う。  
- 売買ロジックや戦略条件、スクリーニング条件を変更したら `/docs/STRATEGY.md` を同時に更新する。  
- 実行手順や検証コマンドを変更したら `/docs/COMMAND.md` を更新する。  
- 変更は小さく段階的に行い、暗黙仕様の追加やロジックの勝手な簡略化をしない。  

---

## ファイル別の役割と参照タイミング

| ファイル | 役割 | 参照するタイミング |
|---|---|---|
| `README.md` | プロジェクト説明・概要 | プロジェクト全体を把握したいとき |
| `/docs/STRATEGY.md` | 売買ロジック仕様（Python ロジックの基準） | 売買ロジックを変更するとき、条件の追加・緩和を検討するとき |
| `/docs/COMMAND.md` | 開発で使用するコマンド集 | 実装後にコマンドでデバッグ・動作確認するとき |

## 参照フロー

1. まず `README.md` を読んで目的・アーキテクチャ・基本原則を確認する。  
2. 売買ロジック関連の変更は、必ず `/docs/STRATEGY.md` を正として仕様と整合させる。
3. 実装後の確認・デバッグは `/docs/COMMAND.md` のコマンドを使って実施する。

---

## 実装時チェック

- 仕様確認: `README.md` / `/docs/STRATEGY.md`
- 実装: 既存アーキテクチャを維持して最小差分で変更
- 検証: `/docs/COMMAND.md` のコマンドで再現可能に確認
- 反映: 必要に応じて関連ドキュメントを更新

---

## 高レベルアーキテクチャ（要点）

- python/: バックテスト／スクリーニングの本体（CLI で実行、出力は CSV / PNG）。
- backend/: FastAPI サーバが python の出力ディレクトリを読み、JSON（チャートは base64 Data URI）で返す。
- frontend/: React + TypeScript による表示層（計算ロジックは禁止、API からの表示専用）。
- 出力パス例: `python/output/backtest/backtest_YYYY-MM-DD_to_YYYY-MM-DD_YYYYmmdd-HHMMSS/`（trades.csv, ticker_stats.csv, charts/*.png 等）。
- データフロー: python -> output files -> FastAPI -> フロントエンド（REACT_APP_API_URL で接続先を切替）。

---

## リポジトリ固有の主要規約（Copilot が従うべき事項）

- TDD 優先: 新しいロジックや script 変更はまずテストを書く（RED→GREEN→REFACTOR）。
- テスト要件: 外部 API は必ずモック、ネットワーク禁止、テストは短時間で完了（目安: 5 秒以内）。
- 出力契約: CSV / DataFrame の必須カラム（例: `ticker, exchange, sector, stage`）は明示し、変更時は契約テストを追加。
- ステージ分離: Stage1 / Stage2 / Backtest は疎結合。下流は上流の出力のみ参照。
- ログ出力: `print()` 禁止。構造化ロガーを使用すること。
- DataFrame 安全チェック必須: `if df is None or df.empty: return` のようなガードを入れる。
- 機密情報: コードにハードコード禁止。環境変数を使う。
- Git / PR: Conventional Commits、main 直push 禁止、PR はテスト通過必須。

---

## API / 型・コンパチビリティに関する注意

- API は現状 JSON + charts: `data:image/png;base64,...` で返却される（フロントはこれをそのまま表示）。この交換形式を勝手に変更しないこと。変更する場合は backend の TypeScript 型定義と tests を同時に更新する。
- フロントは計算ロジックを持たない（表示専用）。重いロジックは python 側で実行させる。

---

## Copilot への具体的な指示（行動方針）

- 設計を壊す変更をしない。大きな構造変更は計画 (plan) を立て、ユーザに確認する。
- 変更提案には必ず対応するテスト（ユニットまたはスモーク）を添付する。
- API 変更提案はバックエンドとフロント両方の型/実装差分を示すこと。
- 変更は小さく段階的に行うこと。大きな変更は分割して提案する。

---
##　開発ワークフロー
以下の開発ワークフローを厳密に守ること。

###　Step 1: 計画（PLAN）
リポジトリ全体を分析し、実装計画を作成してください。
実装計画は /home/fpxszk/code/Invest/docs/PLAN.md に記載してください。

計画には以下を含めてください：
- 変更するファイル
- 新規作成するファイル
- 実装内容
- 影響範囲

計画はチェックボックスを使用してタスク形式で記載してください（例: - [ ] backend/api.py に GET /api/new-endpoint を追加する）。
計画を提示した後、ask_user を呼び出してユーザーの確認を待ってください。

ユーザーの承認があるまで実装を開始してはいけません。

###　Step 2: 実装（IMPLEMENT）
docs\PLAN.mdの承認された計画に基づいてコードを実装してください。

- 必要なファイルを作成・変更してください
- README.md に書かれている設計ルールを必ず守ってください
- 既存コードの設計を壊さないようにしてください

実装が完了したら ask_user を呼び出して確認を待ってください。

###　Step 3: レビュー（REVIEW）
自分が書いたコードをレビューしてください。

確認する内容：
- バグがないか
- README.md のルールに従っているか
- 戦略ロジックを壊していないか
- 不要な複雑化をしていないか

レビューが終わったら ask_user を呼び出して確認を待ってください。

###　Step 4: コミット（COMMIT）
必ず開発ブランチを作成し、そちらに対してGitコミットを作成してください。
必ず現在の作業ブランチからfeature/taskX を作成してください。
main から直接作らないでください。
コミットメッセージは Conventional Commits 形式を使用してください。

例：
feat: add stage2 screening filter
fix: correct backtest entry logic
refactor: simplify chart generation

コミット作成後、ask_user を呼び出して push してよいか確認してください。

###　Step 5: Push
ユーザーの承認後、開発ブランチを push してください。
また、変更内容を分かりやすく記載したPull Request を作成してください。

###　Step 6: 改善提案（IMPROVEMENT）
タスク完了後、リポジトリを再度分析してください。

以下を提案してください：

- コード改善
- パフォーマンス改善
- テスト追加
- 設計改善
- UI改善

改善案を提示した後、ask_user を呼び出して次の作業を開始してよいか確認してください。

### 重要ルール
以下を必ず守ってください：

- ask_user を呼び出したら必ずユーザーの入力を待つこと
- ユーザー承認なしに実装を進めないこと
- README.md の設計を壊さないこと
- STRATEGY.md のトレーディングロジックを勝手に変更しないこと
- 未来データ参照（look-ahead bias）を絶対に導入しないこと

---










