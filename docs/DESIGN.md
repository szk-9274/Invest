# DESIGN

目的
- 本ディレクトリに格納する設計ドキュメントのガイドラインと索引を定義します。

構成と運用
- design-docs/: システム設計上の決定や原則、トレードオフを記録します。設計判断の根拠を残し、将来の見直しに備えます。
- exec-plans/: 実行計画の追跡用。現在進行中(active)、完了(completed)、技術的負債のトラッキングを分離します。
- generated/: 自動生成ドキュメントを置く場所。手動編集は禁止。
- product-specs/: ユーザー向けの機能仕様・UI 仕様を格納します。
- references/: 外部ライブラリやツールの短い要約（LLM 向け）を置きます。

運用ルール（簡易）
- design-docs は変更時に authors を記載すること。
- exec-plans/active は実行責任者と期限を明記すること。
- generated 内は CI で自動更新する仕組みを作ること（現状は手動生成の placeholder）。
- product-specs は UI 実装時に必ず参照し、差分が出たら PR に該当仕様の更新を添付すること。
