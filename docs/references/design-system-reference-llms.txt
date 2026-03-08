Design system reference (LLM 向け要約)

- lightweight-charts: 軽量ローソク足描画ライブラリ。canvas ベースで高速。描画順や resize に注意。
- Plotly: 高機能だがバンドルが大きい。layout.images の layer 指定や opacity 設定が重要。
- mplfinance/matplotlib: Python 側でのチャート描画と PNG 生成に使用。

用途別メモ:
- チャートの合成: PNG 背景を Plotly の layout.images に置くか、frontend で <img> 背景に canvas を重ねる方法がある。
- LLM 参照: この要約は LLM がライブラリ用途を素早く参照するための短いメモとして使ってください。
