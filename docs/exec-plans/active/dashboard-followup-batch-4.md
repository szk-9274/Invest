# 実装計画: ダッシュボード改善バッチ 4

- フェーズ: バックテストダッシュボード改善 Phase 6
- プラン: Issue #64 に基づく baseline alias / portrait pipeline 改善
- 責任者: Copilot
- 目的: Mark Minervini baseline の結果選択を暗黙値ではなく明示契約へ寄せ、trader portrait の正式 asset 化と視覚回帰検知を進める。
- issue 連携: `#64 Formalize baseline strategy aliasing and trader portrait pipeline`
- 進捗: planning

## 前提
- 現在は `TraderStrategiesPage` が `minervini-trend` を `undefined` に変換して baseline 結果を取得している。
- trader portrait は placeholder asset で、正式画像・最適化形式・読み込み方針は未確定である。
- jsdom ベースの E2E は構造回帰には効くが、見た目崩れ検知は弱い。

## 変更・作成するファイル
- 更新候補: `backend/services/strategy_profiles.py`, `backend/api/backtest.py`, `backend/schemas/backtest.py`
- 更新候補: `python/config/params.yaml`
- 更新候補: `frontend/src/pages/TraderStrategiesPage.tsx`
- 更新候補: `frontend/src/domain/traderProfiles.ts`
- 更新候補: `frontend/src/components/TraderAvatar.tsx`
- 更新候補: visual regression / screenshot test 関連ファイル
- 更新候補: `README.md`, `COMMAND.md`, portrait asset 運用に関する design doc

## 実装内容
- 1. strategy profile metadata に baseline alias / result selector を表す明示フィールドを追加する。
- 2. frontend の Minervini baseline 表示を backend metadata ベースへ置き換える。
- 3. trader portrait の正式 asset/pipeline を決め、読み込み戦略を整理する。
- 4. portrait / badge / alignment を検知できる visual regression または screenshot 系テストを導入する。
- 5. docs と asset 命名規約を揃え、将来の trader 追加手順を簡潔にする。

## 影響範囲
- strategy profile API / params.yaml / frontend selector
- trader portrait asset と UI 表示
- dashboard visual regression / screenshot test
- docs / command / asset 運用

## 実装ステップ
### Task 1: RED
- [ ] baseline alias metadata を前提にした backend/frontend test を追加する
- [ ] portrait と baseline badge の視覚回帰を検知する test を追加する

### Task 2: GREEN
- [ ] backend strategy profile metadata に明示フィールドを追加する
- [ ] frontend の baseline 取得ロジックを metadata ベースへ置き換える
- [ ] portrait asset/pipeline を正式運用に寄せる

### Task 3: REFACTOR
- [ ] docs / asset / metadata 命名を共通化する
- [ ] baseline badge と portrait 表示の責務境界を整理する

### Task 4: 検証
- [ ] backend/frontend tests、build、docs check を通す
- [ ] visual regression / screenshot 系の確認手順を整理する

## 注意点
- 現行の Minervini baseline 表示を壊さない。
- portrait asset 変更でリポジトリ容量や初期表示コストを悪化させない。
- backend metadata 変更時は OpenAPI 契約の追従を忘れない。
