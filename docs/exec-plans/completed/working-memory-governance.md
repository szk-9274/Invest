# 実装計画: 長期記憶・文脈維持ルールの文書整理

- タイトル: 長期記憶・文脈維持ルールの文書整理
- 責任者: Copilot
- 目的: 長期記憶・文脈維持ルールを `.github/copilot-instructions.md` から適切な docs へ再配置し、`docs/working-memory/` をセッション記憶不足時の参照先、`docs/decision-log/` を設計判断の正式記録先として位置づけつつ、最小限の instructions と一貫した文書導線を整える。
- 進捗: review-complete, commit-pending

## 変更・作成するファイル
- 更新候補: `.github/copilot-instructions.md`, `docs/DOCUMENTATION_SYSTEM.md`
- 作成候補: `docs/decision-log/index.md`, `docs/working-memory/index.md`, `docs/working-memory/session-logs/index.md`, `docs/working-memory/summaries-lv1/index.md`, `docs/working-memory/summaries-lv2/index.md`
- 必要に応じて更新: `scripts/doc_gardening.py`, `scripts/check_docs.py`, `docs/generated/doc-inventory.md`, `docs/exec-plans/active/index.md`

## 実装内容
- 長期記憶・文脈維持ルールの詳細な運用説明は `docs/DOCUMENTATION_SYSTEM.md` へ集約する。
- `.github/copilot-instructions.md` では詳細説明を避け、セッション記憶が不足した場合のみ `docs/decision-log/`、`docs/working-memory/`、`docs/exec-plans/active/` を参照する最小限の導線だけを残す。
- `docs/DOCUMENTATION_SYSTEM.md` に、working-memory を通常参照ではなくフォールバック参照先として扱うこと、`docs/decision-log/` を設計判断の正式記録先とすること、参照優先順位、長時間作業終了時の更新義務を追記する。
- 必要なら `docs/decision-log/` と `docs/working-memory/` の索引とサブディレクトリを追加し、記録先の役割だけを明文化する。
- 文書生成/検証スクリプトへの影響を確認し、必要な範囲のみ更新して doc inventory と整合させる。

## 影響範囲
- AI 向け運用ルールの配置と参照条件
- docs 配下の知識導線と索引
- ドキュメント整合性チェックと生成物

## 実装ステップ
- [x] 現行の instructions / DOCUMENTATION_SYSTEM / docs 生成ルールを調査し、適切な配置先を決める
- [x] `copilot-instructions.md` を最小限の内容へ整理し、詳細は docs 参照へ寄せる
- [x] `docs/DOCUMENTATION_SYSTEM.md` に長期記憶運用ルールを記載し、必要なら `docs/decision-log/` と `docs/working-memory/` には記録先の役割だけを追記する
- [x] 必要な索引・ディレクトリ・生成/検証スクリプトを更新し、文書体系全体の整合性を取る
- [x] 変更後に関連チェックを実行し、プランの進捗と整合性を更新する

## 注意点
- `.github/copilot-instructions.md` は要約と参照導線に留め、運用詳細の重複を避ける
- `docs/working-memory/` は詳細ルールの説明場所ではなく、セッション記憶不足時の参照先であることを崩さない
- `docs/decision-log/` は `working-memory/` と分離し、重要な設計判断の正式記録先として扱う
- `docs/generated/*` は手編集せず、必要なら生成スクリプト経由で更新する
- 空ディレクトリだけを追加せず、必要な場合は index.md を置いて役割を明文化する
