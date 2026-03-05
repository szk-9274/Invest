 まず次の3つの計画を詳細までレビューして問題点がないかを確認して
  「/dashboard のチャート実装（Plotlyベース）  docs/PLAN/PLAN.md→ /home の UI 実装（metaplanet.jp/en 
    準拠）docs/PLAN/home-assets.md→ サイト全体の日本語化（右上トグル）plan-sitewide-i18n.md」

  問題点があれば修正し、修正後そのPLANをもとに実装を開始して。
    各大タスクは必ず STEP 1〜6 を順守して実行してください：STEP 1 PLAN — 変更箇所・影響範囲・受け入れ基準・参照アセットを明記して 
  ask_user 
    承認を得ること。STEP 2 IMPLEMENT — 承認後に feat/<todo-id>
    ブランチを作成し最小差分で実装（TDD を優先、vitest と必要に応じて Playwright E2E を追加）、/dashboard のチャートは Plotly を用い 
    /dashboard のみに適用、画像等はライセンス確認後のみ
    docs/PLAN/assets に保存して repo へコミットすること。STEP 3 REVIEW — 
    自己レビューで機能・アクセシビリティ・パフォーマンス・ライセンスを検証し結果を記載、STEP 4 COMMIT — Conventional Commits
    形式でコミットし各コミット末尾に必ず「Co-authored-by: Copilot 223556219+Copilot@users.noreply.github.com (
    mailto:223556219+Copilot@users.noreply.github.com)」を付記、
  コミットは３つのタスクがあるので一つにまとめず分割してほしい
  STEP 5 PUSH — リモートへ push し PR を作成、PR 
    に変更点・参照ファイル・スクショを添付、STEP 6 IMPROVEMENT — PR
    に改善案を記載して次タスクを todos に登録すること。
    重要ルール：ask_user を呼び出したら必ずユーザーの応答を待つこと、変更は最小限に留めること、ヘッドレスで取得した assets は 
    docs/PLAN/assets に保存して docs/PLAN/assets-licenses.md
    に出典・ライセンスを記録すること、作業中は todos を更新して進捗を残すこと。
