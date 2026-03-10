# Decision log: local manifest based experiment tracking

- Status: accepted
- Date: 2026-03-10

## Context
Invest には既に yfinance ベースのデータ取得、ルール判定、バックテスト、FastAPI、React ダッシュボードが存在していた。一方で、run ごとの実行条件・評価指標・成果物一覧を一貫して残す仕組みが弱く、比較検証と後追い確認がしにくかった。

## Decision
Qlib の recorder / workflow 思想を最小限で取り込み、各バックテスト run に `run_manifest.json` を保存し、`python/output/backtest/registry.json` に run 一覧を集約する。外部サービスや MLflow は導入せず、ローカル JSON のみで完結させる。

## Consequences
- backend は manifest を読んで run metadata を API に含められる。
- frontend は実験名・戦略名・rule profile・benchmark 状態を比較 UI の土台として表示できる。
- 将来の軽量 scorer 導入や実験比較 UI はこの metadata 構造を基準に拡張できる。
- 一方で、高度な検索・可視化・履歴管理は将来の追加実装が必要。
