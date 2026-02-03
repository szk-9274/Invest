---    
# Everything Claude Code：ロングフォーム・ガイド  
  
\!\[Header: The Longform Guide to Everything Claude Code\] (./assets/images/longform/01-header.png)  
  
---  
  
> **前提条件**: このガイドは [The Shorthand Guide to Everything Claude Code](./the-shortform-guide.md) を土台にしています。まだスキル、フック、サブエージェント、MCP、プラグインをセットアップしていない場合は、先にそちらを読んでください。  
  
\!\[Reference to Shorthand Guide\] (./assets/images/longform/02-shortform-reference.png)    
*The Shorthand Guide - まずこれを読む*  
  
ショートハンドガイドでは、基礎となるセットアップ（スキルとコマンド、フック、サブエージェント、MCP、プラグイン、そして効果的な Claude Code ワークフローの背骨となる設定パターン）を扱いました。あれはセットアップガイドであり、ベースとなるインフラです。  
  
このロングフォームガイドでは、「生産的なセッション」と「無駄の多いセッション」を分けるテクニックに踏み込みます。ショートハンドガイドを読んでいないなら、まず戻って設定を整えてください。以降の内容は、スキル、エージェント、フック、MCP がすでに設定済みで動作している前提です。  
  
ここで扱うテーマは、トークン経済（token economics）、メモリ永続化、検証パターン、並列化戦略、そして再利用可能なワークフローを構築することによる複利効果です。これらは、10か月以上の毎日の利用の中で磨き込んできたパターンであり、開始1時間でコンテキスト腐敗（context rot）に悩まされるか、何時間も生産的に進められるかの差になります。  
  
ショートハンド/ロングフォーム両ガイドで扱う内容は GitHub にあります：`github.com/affaan-m/everything-claude-code`  
  
---  
  
## Tips & Tricks  
  
### 置き換え可能な MCP はある（コンテキストウィンドウを空けられる）  
  
バージョン管理（GitHub）、データベース（Supabase）、デプロイ（Vercel、Railway）などの MCP は、その多くが「既存の強力な CLI を MCP が包んでいるだけ」というケースです。MCP は便利なラッパーですが、コストもあります。  
  
MCP を使わずに（そしてそれに伴うコンテキストウィンドウの縮小も避けて）CLI を MCP のように扱いたいなら、その機能をスキル/コマンドにまとめることを検討してください。MCP が提供している「便利ツール」を剥がし取り、それらをコマンド化します。  
  
例：GitHub MCP を常時ロードする代わりに、`gh pr create` を好みのオプションでラップした `/gh-pr` コマンドを作る。Supabase MCP にコンテキストを食わせる代わりに、Supabase CLI を直接使うスキルを作る。  
  
Lazy loading により、コンテキストウィンドウの問題は概ね解決しました。しかし、トークン使用量とコストは同じようには解決しません。CLI + スキルのアプローチは、依然としてトークン最適化手法です。  
  
---  
  
## 重要事項（IMPORTANT STUFF）  
  
### コンテキストとメモリ管理  
  
セッションをまたいで記憶を共有するには、進捗を要約してチェックインし、それを `.claude` フォルダ配下の `.tmp` ファイルに保存し、セッション終了まで追記していくスキル/コマンドが最も堅実です。翌日はそれをコンテキストとして利用し、中断したところから再開できます。各セッションごとに新しいファイルを作り、古いコンテキストが新しい作業に混ざらないようにしてください。  
  
\!\[Session Storage File Tree\] (./assets/images/longform/03-session-storage.png)    
*セッション保存の例 -> https://github.com/affaan-m/everything-claude-code/tree/main/examples/sessions*  
  
Claude は現在の状態を要約したファイルを作成します。内容を確認し、必要なら修正を依頼してから、新しい会話を開始します。新しい会話では、そのファイルパスを渡すだけでOKです。特に、コンテキスト制限に達して複雑な作業を継続したいときに有用です。これらのファイルには次を含めるべきです：  
  
- うまくいったアプローチ（根拠/証拠つきで検証可能に）  
- 試したがうまくいかなかったアプローチ  
- まだ試していないアプローチと、残っている作業  
  
**戦略的にコンテキストをクリアする（Clearing Context Strategically）:**    
計画（plan）を固め、コンテキストをクリアしたら（今は Claude Code の plan mode の既定オプション）、以降は計画に沿って実行できます。探索で溜まったコンテキストが実行には不要になったときに有効です。戦略的コンパクション（strategic compacting）をするなら、オートコンパクトを無効化してください。論理的な区切りで手動コンパクトするか、それを行うスキルを作成します。  
  
**上級：動的な System Prompt 注入（Dynamic System Prompt Injection）**    
私が拾ったパターンのひとつ：CLAUDE.md（ユーザースコープ）や `.claude/rules/`（プロジェクトスコープ）にすべてを入れて「毎セッションロード」するのではなく、CLI フラグで動的にコンテキストを注入します。  
  
```bash  
claude --system-prompt "$(cat memory.md)"  
```  
  
これにより、「どのコンテキストをいつロードするか」をより外科的に制御できます。system prompt の内容はユーザーメッセージより権限が強く、ユーザーメッセージはツール結果より権限が強いです。  
  
**実用的なセットアップ:**  
  
```bash  
# Daily development  
alias claude-dev='claude --system-prompt "$(cat ~/.claude/contexts/dev.md)"'  
  
# PR review mode  
alias claude-review='claude --system-prompt "$(cat ~/.claude/contexts/review.md)"'  
  
# Research/exploration mode  
alias claude-research='claude --system-prompt "$(cat ~/.claude/contexts/research.md)"'  
```  
  
**上級：メモリ永続化フック（Memory Persistence Hooks）**    
多くの人が知らない、メモリに効くフックがあります：  
  
- **PreCompact Hook**: コンテキスト圧縮の直前に、重要な状態をファイルに保存  
- **Stop Hook（セッション終了）**: セッション終了時に学びをファイルへ永続化  
- **SessionStart Hook**: 新しいセッションで、前回のコンテキストを自動ロード  
  
これらのフックは私が実装済みで、リポジトリにあります：`github.com/affaan-m/everything-claude-code/tree/main/hooks/memory-persistence`  
  
---  
  
### 継続学習 / メモリ（Continuous Learning / Memory）  
  
同じプロンプトを何度も繰り返し、Claude が同じ問題にぶつかったり、聞き飽きた回答をしてくるなら——そのパターンはスキルに追記されるべきです。  
  
**問題:** トークンの無駄、コンテキストの無駄、時間の無駄。    
**解決策:** Claude Code が「自明ではない何か」（デバッグ技法、回避策、プロジェクト固有パターンなど）を見つけたら、その知識を新しいスキルとして保存します。次回、似た問題が起きたとき、そのスキルが自動的にロードされます。  
  
これを行う継続学習スキルを作っています：`github.com/affaan-m/everything-claude-code/tree/main/skills/continuous-learning`  
  
**なぜ UserPromptSubmit ではなく Stop Hook か:**    
設計上の重要な判断は、UserPromptSubmit ではなく **Stop hook** を使うことです。UserPromptSubmit はすべてのメッセージで走るため、毎回のプロンプトに遅延が乗ります。Stop はセッション終了時に一度だけ走るため軽量で、セッション中にあなたを遅くしません。  
  
---  
  
### トークン最適化（Token Optimization）  
  
**主要戦略：サブエージェント・アーキテクチャ**    
使うツールを最適化し、「そのタスクに十分な最安モデル」を委譲できるようサブエージェント設計を行います。  
  
**モデル選定クイックリファレンス:**  
  
\!\[Model Selection Table\] (./assets/images/longform/04-model-selection.png)    
*よくあるタスクに対するサブエージェントの仮想的な割り当てと、その理由*  
  
| タスク種別 | モデル | 理由 |  
| --- | --- | --- |  
| 探索/検索 | Haiku | 高速・安価・ファイル探しには十分 |  
| 単純編集 | Haiku | 単一ファイル変更、指示が明確 |  
| 複数ファイル実装 | Sonnet | コーディングのバランスが最良 |  
| 複雑なアーキテクチャ | Opus | 深い推論が必要 |  
| PR レビュー | Sonnet | 文脈を理解し、ニュアンスを拾える |  
| セキュリティ分析 | Opus | 脆弱性を見落とす余裕がない |  
| ドキュメント執筆 | Haiku | 構造が単純 |  
| 複雑バグのデバッグ | Opus | システム全体を頭に保持する必要 |  
  
コーディングタスクの 90% は Sonnet をデフォルトにします。初回の試みが失敗した、5ファイル以上にまたがる、アーキテクチャ判断が必要、セキュリティクリティカル——こういう場合に Opus へ上げます。  
  
**価格の参考:**  
  
\!\[Claude Model Pricing\] (./assets/images/longform/05-pricing-table.png)    
*Source: https://platform.claude.com/docs/en/about-claude/pricing*  
  
**ツール別最適化:**    
grep を mgrep に置き換えると、従来の grep/ripgrep と比べて平均で ~50% トークン削減になることがあります：  
  
\!\[mgrep Benchmark\] (./assets/images/longform/06-mgrep-benchmark.png)    
*50タスクのベンチマークで、mgrep + Claude Code は grep ベースのワークフローより ~2倍少ないトークンで、同等以上の評価品質。Source: https://github.com/mixedbread-ai/mgrep*  
  
**モジュール化コードベースの利点:**    
主要ファイルが数千行ではなく数百行に収まるようなモジュール化されたコードベースは、トークンコスト最適化にも、初回で正しくタスクを終える確率にも効きます。  
  
---  
  
### 検証ループ（Verification Loops）と Evals  
  
**ベンチマーク用ワークフロー:**    
スキルあり/なしで同じ依頼をして、出力差分を比較します。会話を fork し、片方ではスキルなしで新しい worktree を用意し、最後に diff を取り、何がログされたかを確認します。  
  
**Eval パターンの種類:**  
- **チェックポイント型 Evals**: 明確なチェックポイントを置き、定義済み基準に照らして検証し、次へ進む前に修正する  
- **継続型 Evals**: N 分ごと、または大きな変更の後に走らせる（フルテストスイート + lint）  
  
**主要メトリクス:**  
  
```text  
pass@k: k 回の試行のうち少なくとも 1 回成功  
        k=1: 70%  
        k=3: 91%  
        k=5: 97%  
  
pass^k: k 回すべて成功しなければならない  
        k=1: 70%  
        k=3: 34%  
        k=5: 17%  
```  
  
「とにかく動けばよい」なら **pass@k**。「一貫性が本質」なら **pass^k** を使います。  
  
---  
  
## 並列化（PARALLELIZATION）  
  
マルチ Claude のターミナル構成で会話を fork するときは、fork と元会話それぞれのスコープを明確にしてください。コード変更の重なりは最小化するのが目標です。  
  
**私の好みのパターン:**    
メインチャットはコード変更に使い、fork はコードベースの現状に関する質問、あるいは外部サービスの調査に使います。  
  
**任意のターミナル数について:**    
  
\!\[Boris on Parallel Terminals\] (./assets/images/longform/07-boris-parallel.png)    
*Boris（Anthropic）による複数 Claude インスタンス運用の話*  
  
Boris は並列化のコツを語っていて、ローカルに 5、上流に 5 などの提案もしています。私は「任意の台数を決めて走らせる」ことは勧めません。ターミナルを増やすのは、真の必要性があるときに限るべきです。  
  
あなたのゴールはこうです：**必要最小限の並列化で、どれだけ多くを成し遂げられるか。**  
  
**並列インスタンスのための Git Worktrees:**  
  
```bash  
# Create worktrees for parallel work  
git worktree add ../project-feature-a feature-a  
git worktree add ../project-feature-b feature-b  
git worktree add ../project-refactor refactor-branch  
  
# Each worktree gets its own Claude instance  
cd ../project-feature-a && claude  
```  
  
インスタンスをスケールし、かつ複数の Claude が互いに重なるコードを触るなら、git worktrees を使い、各インスタンスに非常に明確な計画を持たせることが不可欠です。`/rename <name here>` で各チャットに名前を付けてください。  
  
\!\[Two Terminal Setup\] (./assets/images/longform/08-two-terminals.png)    
*初期セットアップ：左＝コーディング、右＝質問。/rename と /fork を使う*  
  
**カスケード・メソッド（The Cascade Method）:**    
複数の Claude Code インスタンスを走らせるときは、「カスケード」パターンで整理します：  
  
- 新しいタスクは右側の新タブで開く  
- 左から右へ、古いものから新しいものへスイープする  
- 同時に集中するのは最大 3〜4 タスクまで  
  
---  
  
## 土台作り（GROUNDWORK）  
  
**2インスタンス起動パターン（The Two-Instance Kickoff Pattern）:**    
私のワークフロー管理では、空のリポジトリを 2 つの Claude インスタンスを開いた状態で始めるのが好きです。  
  
**インスタンス1：足場（Scaffolding）エージェント**  
- スキャフォールド/土台を敷く  
- プロジェクト構造を作る  
- 設定（CLAUDE.md、rules、agents）を整える  
  
**インスタンス2：深掘り調査（Deep Research）エージェント**  
- すべてのサービスへ接続、Web検索  
- 詳細な PRD を作る  
- アーキテクチャの mermaid 図を作る  
- 実ドキュメントの抜粋つきで参考資料をまとめる  
  
**llms.txt パターン:**    
もし利用可能なら、多くのドキュメント参照先で、ドキュメントページに到達した後に `/llms.txt` を叩くと `llms.txt` が見つかることがあります。これは LLM 向けに最適化されたクリーンなドキュメントです。  
  
**思想：再利用可能パターンを作る（Build Reusable Patterns）**    
@omarsar0 より：「初期に再利用可能なワークフロー/パターンを作ることに時間を使った。作るのは面倒だが、モデルやエージェントのハーネスが改善されるにつれて、すさまじい複利効果が出た。」  
  
**投資すべきもの:**  
- サブエージェント  
- スキル  
- コマンド  
- 計画（planning）パターン  
- MCP ツール  
- コンテキストエンジニアリングのパターン  
  
---  
  
## エージェント / サブエージェントのベストプラクティス  
  
**サブエージェントのコンテキスト問題（The Sub-Agent Context Problem）:**    
サブエージェントは、すべてをダンプせず要約を返すことでコンテキストを節約するために存在します。しかし、オーケストレーター（メイン）はサブエージェントが持たない意味的コンテキストを持っています。サブエージェントが知っているのは「文字通りのクエリ」であり、依頼の背後にある **目的（PURPOSE）** ではありません。  
  
**反復的リトリーバル（Iterative Retrieval）パターン:**  
1. オーケストレーターがサブエージェントの返答を評価する  
2. 受け入れる前にフォローアップ質問をする  
3. サブエージェントがソースへ戻り、回答を得て返す  
4. 十分になるまでループ（最大 3 サイクル）  
  
**要点:** クエリだけでなく、目的のコンテキストを渡すこと。  
  
**逐次フェーズを持つオーケストレーター:**  
  
```markdown  
Phase 1: RESEARCH (use Explore agent) → research-summary.md  
Phase 2: PLAN (use planner agent) → plan.md  
Phase 3: IMPLEMENT (use tdd-guide agent) → code changes  
Phase 4: REVIEW (use code-reviewer agent) → review-comments.md  
Phase 5: VERIFY (use build-error-resolver if needed) → done or loop back  
```  
  
**重要ルール:**  
1. 各エージェントは「1つの明確な入力」を受け取り「1つの明確な出力」を作る  
2. 出力は次フェーズの入力になる  
3. フェーズを飛ばさない  
4. エージェント間で `/clear` を使う  
5. 中間出力はファイルに保存する  
  
---  
  
## お楽しみ（FUN STUFF / 重要ではないが便利な小ネタ）  
  
### カスタムステータスライン  
`/statusline` で設定できます。Claude は「今は設定がないが作れる」と言い、入れたい情報を聞いてきます。    
参考： https://github.com/sirmalloc/ccstatusline  
  
### 音声文字起こし  
声で Claude Code に話しかけられます。多くの人にとってタイピングより速いです。    
- Mac なら superwhisper、MacWhisper    
- 多少の誤変換があっても、Claude は意図を理解できます  
  
### ターミナルエイリアス  
```bash  
alias c='claude'  
alias gb='github'  
alias co='code'  
alias q='cd ~/Desktop/projects'  
```  
  
---  
  
## マイルストーン  
\!\[25k+ GitHub Stars\] (./assets/images/longform/09-25k-stars.png)    
*1週間未満で GitHub Star 25,000+*  
  
---  
  
## リソース（Resources）  
  
**エージェント・オーケストレーション:**  
- https://github.com/ruvnet/claude-flow - 54+ の特化エージェントを備えたエンタープライズ向けオーケストレーション基盤  
  
**自己改善メモリ（Self-Improving Memory）:**  
- https://github.com/affaan-m/everything-claude-code/tree/main/skills/continuous-learning    
- rlancemartin.github.io/2025/12/01/claude_diary/ - セッション内省（reflection）パターン  
  
**System Prompts 参考:**  
- https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools - system prompt コレクション（Star 110k）  
  
**公式:**  
- Anthropic Academy: anthropic.skilljar.com  
  
---  
  
## 参考文献（References）  
  
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)  
- [YK: 32 Claude Code Tips](https://agenticcoding.substack.com/p/32-claude-code-tips-from-basics-to)  
- [RLanceMartin: Session Reflection Pattern](https://rlancemartin.github.io/2025/12/01/claude_diary/)  
- @PerceptualPeak: Sub-Agent Context Negotiation  
- @menhguin: Agent Abstractions Tierlist  
- @omarsar0: Compound Effects Philosophy  
  
---  
  
*両ガイドで扱う内容はすべて GitHub の [everything-claude-code](https://github.com/affaan-m/everything-claude-code) で利用できます*  