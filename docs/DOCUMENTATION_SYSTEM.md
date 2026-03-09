# DOCUMENTATION_SYSTEM

目的
- このドキュメントは、このリポジトリの知識ベースをどの順番で読むべきか、どこに何を書くべきか、どうやって鮮度を保つかを定義する入口です。
- 大きな単一マニュアルではなく、索引から必要な深さへ進む段階的開示を前提にします。

## 読み始める順番
1. [README.md](../README.md) - プロジェクト全体の概要と起動方法
2. [ARCHITECTURE.md](../ARCHITECTURE.md) - レイヤ責務と配置基準
3. [docs/design-docs/index.md](design-docs/index.md) - 詳細設計の索引
4. [docs/exec-plans/active/index.md](exec-plans/active/index.md) - 現在進行中の実装計画
5. [docs/exec-plans/completed/index.md](exec-plans/completed/index.md) - 完了済みの実装計画
6. [docs/product-specs/index.md](product-specs/index.md) - 仕様書の索引
7. [docs/generated/doc-inventory.md](generated/doc-inventory.md) - 実在するドキュメントと workflow の在庫表

## セッション記憶が不足したときの参照順
- セッション内の記憶が十分な間は `docs/working-memory/` を参照しません。
- 記憶が不足したときだけ、会話ログ全文ではなく要約済みの知識構造を優先して参照します。
- 必ず「上位要約 -> 下位詳細」の順で辿り、`session-logs/` は最終手段に限定します。

1. [docs/decision-log/index.md](decision-log/index.md) - 重要な設計決定と見直し条件
2. [docs/exec-plans/active/index.md](exec-plans/active/index.md) - 現在進行中の実装計画
3. [docs/working-memory/summaries-lv2/index.md](working-memory/summaries-lv2/index.md) - フェーズ単位の要約
4. [docs/working-memory/summaries-lv1/index.md](working-memory/summaries-lv1/index.md) - 週次・タスク単位の要約
5. [docs/working-memory/session-logs/index.md](working-memory/session-logs/index.md) - 日次の圧縮ログ

## 正式な記録先
- ルート:
  - [README.md](../README.md) - 外部向け概要
  - [ARCHITECTURE.md](../ARCHITECTURE.md) - システム構造と責務
  - [COMMAND.md](../COMMAND.md) - 実行コマンドの正本
- `docs/`:
  - `DESIGN.md`, `FRONTEND.md`, `PRODUCT_SENSE.md`, `QUALITY_SCORE.md`, `RELIABILITY.md`, `SECURITY.md`
  - `design-docs/` - なぜその設計にしたかを残す詳細設計
  - `product-specs/` - 期待動作と受け入れ条件
  - `decision-log/` - 重要な設計決定、その理由、見直し条件
    - [docs/decision-log/index.md](decision-log/index.md)
  - `exec-plans/` - 実装計画と技術的負債
    - [docs/exec-plans/active/index.md](exec-plans/active/index.md)
    - [docs/exec-plans/completed/index.md](exec-plans/completed/index.md)
  - `working-memory/` - セッション記憶が不足したときに参照する要約・記録の保管場所
    - [docs/working-memory/index.md](working-memory/index.md)
  - `generated/` - 機械生成される補助ドキュメント
  - `references/` - 外部資料への参照

## 鮮度維持の仕組み
- `python scripts/check_docs.py`
  - 必須ドキュメントの存在
  - Markdown 内部リンクの破損
  - 索引ファイルと生成ドキュメントのドリフト
- `python scripts/doc_gardening.py`
  - [docs/design-docs/index.md](design-docs/index.md)
  - [docs/exec-plans/active/index.md](exec-plans/active/index.md)
  - [docs/exec-plans/completed/index.md](exec-plans/completed/index.md)
  - [docs/product-specs/index.md](product-specs/index.md)
  - [docs/generated/doc-inventory.md](generated/doc-inventory.md)
  を機械的に再生成
- `.github/workflows/ci.yml`
  - push / pull_request でドキュメント整合性チェックを実行
- `.github/workflows/docs-governance.yml`
  - push / pull_request で docs lint を実行
  - schedule / workflow_dispatch で doc-gardening を走らせ、差分があれば自動 PR を作成

## 運用ルール
- 実行手順を変えたら [COMMAND.md](../COMMAND.md) を更新する
- レイヤ責務を変えたら [ARCHITECTURE.md](../ARCHITECTURE.md) を更新する
- 設計判断を追加したら `docs/design-docs/` に記録する
- 仕様を追加したら `docs/product-specs/` に記録する
- 長時間の作業終了時は `docs/working-memory/session-logs/` に要約を保存し、重要な設計判断があれば `docs/decision-log/` に追記し、進行中タスクの進捗を `docs/exec-plans/` に反映する
- 設計変更時は、既存の `docs/decision-log/` と整合性を確認する
- 索引と在庫表は手で編集せず、`python scripts/doc_gardening.py` で同期する
