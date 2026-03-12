# 決定: docs の正本化 — DOCUMENTATION_SYSTEM.md を長期記憶の正本に指定

日付: 2026-03-09
作成者: 自動記録 (Copilot)

## 決定内容
- このリポジトリにおける「長期記憶・文脈維持ルール」の正本を `docs/DOCUMENTATION_SYSTEM.md` とする。`.github/copilot-instructions.md` はリポジトリ内での参照導線（短い導入・参照先）に縮約する。

## 理由
- ドキュメントの一元化により整合性が保ちやすく、機械的同期（`scripts/doc_gardening.py`）や CI によるチェックと連携しやすくなるため。
- 運用上、詳細な運用手順・参照優先順位は docs 内で管理したほうがレビューや自動化に適しているため。

## 影響範囲
- `docs/DOCUMENTATION_SYSTEM.md` を参照するすべての場所（例: .github/copilot-instructions.md の参照文、docs/working-memory の運用ルール記述等）。
- `scripts/doc_gardening.py` / docs-governance ワークフロー（必要に応じて見直し）。

## 見直し条件
- ドキュメント方針や自動化ワークフローを大きく変更する場合（例: doc_gardening の廃止、docs 配置ルールの再設計）。

## 参照
- docs/DOCUMENTATION_SYSTEM.md
- session log: docs/working-memory/session-logs/2026-03-09T16-11-18Z-session-summary.md
- PR: https://github.com/FPXszk/MinerviLism/pull/56

---

(この決定は docs/decision-log/ に記録され、将来の設計見直しの参照資料となります。)
