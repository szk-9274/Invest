# External design references

## 1. Qlib repository

- URL: https://github.com/microsoft/qlib
- 参考にした理由: データ処理・モデル・戦略・バックテスト・記録を疎結合に扱う全体思想を確認するため。
- このプロジェクトにどう活かしたか: `python/experiments/` と `run_manifest.json` / `registry.json` を導入し、Qlib の recorder / workflow のうち軽量で取り込みやすい部分だけを採用した。
- 採用したもの: workflow を config-driven にする考え方、run ごとの記録、strategy/backtest/record 分離の方向性。
- 採用しなかったもの: RD-Agent、外部 MLflow 前提、Qlib 独自データフォーマット全面移行、深層学習中心の構成。

## 2. Qlib Workflow documentation

- URL: https://qlib.readthedocs.io/en/latest/component/workflow.html
- 参考にした理由: execution 単位で data / model / evaluation / record を束ねる設計と YAML ベース設定の考え方が整理されているため。
- このプロジェクトにどう活かしたか: `params.yaml` の役割を明確化し、backtest 実行時に parameter snapshot を `run_manifest.json` に保存する形へ落とし込んだ。
- 採用したもの: 実行条件を明示し、run 単位で保存する考え方。
- 採用しなかったもの: `qrun` 相当の大規模 runner、model 学習ワークフローの全面導入。

## 3. Qlib Data Layer documentation

- URL: https://qlib.readthedocs.io/en/latest/component/data.html
- 参考にした理由: data loader / handler / dataset の責務分離が、既存の `fetcher + indicators + engine` の整理方針に近かったため。
- このプロジェクトにどう活かしたか: `python/backtest/data_preparation.py` を追加し、BacktestEngine からデータ準備責務を切り出した。
- 採用したもの: data preparation を独立責務として分ける考え方、前処理を記録可能にする発想。
- 採用しなかったもの: Qlib bin format、専用 data server、学習用 Dataset 抽象の全面移植。

## 4. Qlib Strategy documentation

- URL: https://qlib.readthedocs.io/en/latest/component/strategy.html
- 参考にした理由: signal / strategy / backtest を切り分ける境界が明確で、今後の軽量 scorer 拡張点を考えるうえで参考になったため。
- このプロジェクトにどう活かしたか: `stage` と `entry` の責務を維持しつつ、manifest に `strategy_name` と `rule_profile` を保存するようにした。
- 採用したもの: strategy を run metadata から識別できる形にすること。
- 採用しなかったもの: TopkDropout のようなポートフォリオ最適化戦略そのものの導入。

## 5. Qlib Recorder documentation

- URL: https://qlib.readthedocs.io/en/latest/component/recorder.html
- 参考にした理由: experiment / recorder の2層構造が、比較検証と後追い確認の最小要件を整理するのに有効だったため。
- このプロジェクトにどう活かしたか: 外部サービスを使わず、ローカル JSON だけで `run_manifest.json` と `registry.json` を維持する軽量 recorder 風の構成にした。
- 採用したもの: run ごとの metrics / params / artifacts 保存。
- 採用しなかったもの: MLflow UI、tracking server 常設、外部依存の可視化基盤。

## 6. Qlib workflow_by_code example

- URL: https://raw.githubusercontent.com/microsoft/qlib/main/examples/workflow_by_code.py
- 参考にした理由: 設定とコードの両方で workflow を組み立てる実例として、今回の段階導入に近かったため。
- このプロジェクトにどう活かしたか: `main.py` から直接大規模 framework を呼ばず、既存 CLI のまま manifest 保存を追加する方針の妥当性確認に使った。
- 採用したもの: workflow を「一発実行」ではなく「既存導線に少しずつ足す」考え方。
- 採用しなかったもの: model 学習や signal analysis record の本格導入。

## 7. Qlib LightGBM workflow config example

- URL: https://raw.githubusercontent.com/microsoft/qlib/main/examples/benchmarks/LightGBM/workflow_config_lightgbm_Alpha158.yaml
- 参考にした理由: experiment / dataset / strategy / backtest の YAML 構造が、将来の CPU 軽量モデル導入余地を考える参考になったため。
- このプロジェクトにどう活かしたか: 今回は学習機能は入れず、将来 `strategy_name` / `rule_profile` に加えて scorer を差し替えやすい metadata 構造だけ先に入れた。
- 採用したもの: config で比較条件を明文化する発想。
- 採用しなかったもの: LightGBM 学習自体の本格導入。

## 8. Metaplanet corporate site

- URL: https://metaplanet.jp/jp
- 参考にした理由: localhost 可視化のホーム/ダッシュボード導線で、暗い背景に強いタイポと大きめの CTA を置くトーンを揃えるため。
- このプロジェクトにどう活かしたか: コーポレートのヒーロー構成をそのまま写さず、`HomeLanding` のヒーローセクション、濃紺ベースの配色、丸い CTA、カード境界の見せ方として再解釈した。
- 採用したもの: ダークヒーロー、強い見出し、青/オレンジ系アクセント、カード境界の見せ方。
- 採用しなかったもの: 実画像やブランド固有アセット、IR 専用の導線や文言。
- 実装に反映した箇所: `frontend/src/pages/HomeLanding.tsx`

## 9. Metaplanet Analytics home

- URL: https://analytics.metaplanet.jp/?lang=ja&tab=home
- 参考にした理由: 実験一覧、主要 KPI、比較カードを 1 画面で俯瞰する情報階層が今回の localhost ダッシュボード要件に近かったため。
- このプロジェクトにどう活かしたか: 上部に KPI 概要、その下に比較パネルと実験一覧テーブルを置く構成へ落とし込み、既存の `/dashboard/run` を overview 兼 run 管理画面として再構成した。
- 採用したもの: KPI カードの先頭配置、比較ビューの横並び、テーブル中心の experiment browsing。
- 採用しなかったもの: 既存 SaaS のタブ構成そのもの、固有のブランド KPI やバックエンド依存導線。
- 実装に反映した箇所: `frontend/src/pages/BacktestRunPage.tsx`, `frontend/src/components/BacktestSummary.tsx`, `frontend/src/components/ConditionComparisonPanel.tsx`, `frontend/src/components/ExperimentListTable.tsx`

## 10. Metaplanet Analytics charts

- URL: https://analytics.metaplanet.jp/?lang=ja&tab=charts
- 参考にした理由: エクイティ、ドローダウン、シグナルのような複数系列をカード状に分けて詳細確認する構成の参考にしたため。
- このプロジェクトにどう活かしたか: 1 枚の巨大チャートに寄せず、`BacktestVisualizationPanel` で equity / drawdown / signal events を分割し、既存ギャラリーや trade table と並べても読みやすい構成へ再解釈した。
- 採用したもの: 詳細チャートをカードごとに分ける構成、指標と詳細チャートの上下分離、マーカーによる entry / exit の見せ方。
- 採用しなかったもの: 実データ固有の注釈、サイト固有の UI コンポーネントやブランド文脈。
- 実装に反映した箇所: `frontend/src/pages/BacktestAnalysisPage.tsx`, `frontend/src/components/BacktestVisualizationPanel.tsx`
