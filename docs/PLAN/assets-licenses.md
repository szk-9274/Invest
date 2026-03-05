# assets-licenses

更新日: 2026-03-05

## 目的

`/home` 実装で参照する外部アセットの出典・ライセンス状態・保存先を記録する。
ライセンス未確定のアセットは本番コミット対象にしない。

## 記録表

| asset | source_url | intended_use | license_status | local_path | notes |
|---|---|---|---|---|---|
| Hero background | https://metaplanet.jp//images/planets-hero.jpeg | /home Hero 背景 | pending | docs/PLAN/assets/ | 要利用許諾確認 |
| Light logo `_012.svg` | https://metaplanet.jp/images/logos/light/_012.svg | /home Header/Footer ロゴ | pending | docs/PLAN/assets/ | 要利用許諾確認 |
| Dark logo `_012.svg` | https://metaplanet.jp/images/logos/dark/_012.svg | /home ダーク背景ロゴ | pending | docs/PLAN/assets/ | 要利用許諾確認 |
| Partner logo `bitcoin.jp-white.svg` | https://metaplanet.jp/images/partners/bitcoin.jp-white.svg | /home 掲載ロゴ | pending | docs/PLAN/assets/ | 許諾未確認時は placeholder 使用 |
| LinkedIn icon | https://metaplanet.jp/images/companies/linkedin-icon.svg | /home SNS アイコン | pending | docs/PLAN/assets/ | 代替アイコン検討可 |
| Home implementation screenshot | local (`/home` on localhost) | Task2 PR 添付用 | approved | docs/PLAN/assets/home_task2.png | ローカル実装の検証画像 |

## 運用ルール

1. `license_status` が `approved` になるまで、実装では placeholder を使う。
2. headless 取得物（スクリーンショット・resource JSON）は検証資料として `docs/PLAN/assets/` に保存してよい。
3. ライセンス判定更新時は本ファイルを先に更新してからコードへ反映する。
