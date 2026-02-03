---    
# Everything Claude Code：ショートハンド・ガイド  
  
\!\[Header: Anthropic Hackathon Winner - Tips & Tricks for Claude Code\] (./assets/images/shortform/00-header.png)  
  
---  
  
**2月の実験的ロールアウト以来、Claude Code を熱心に使い続けており、[@DRodriguezFX](https://x.com/DRodriguezFX) と一緒に [zenith.chat](https://zenith.chat) を（完全に Claude Code だけで）作って、Anthropic x Forum Ventures ハッカソンで優勝しました。**    
以下は、10か月間の毎日の使用で固まった私の完全なセットアップです：スキル、フック、サブエージェント、MCP、プラグイン、そして実際に機能するもの。  
  
---  
  
## スキルとコマンド  
  
スキルはルールのように動作しますが、特定のスコープやワークフローに限定されます。特定のワークフローを実行したいときに使う「プロンプトのショートハンド」です。    
Opus 4.5 で長時間コーディングしたあと、デッドコードや散らかった `.md` ファイルを掃除したい？ `/refactor-clean` を実行。テストが必要？ `/tdd`、`/e2e`、`/test-coverage`。スキルには「codemap（コードマップ）」も含められます。これは、探索でコンテキストを消費せずに、Claude がコードベースを素早く辿れるようにする仕組みです。  
  
\!\[Terminal showing chained commands\] (./assets/images/shortform/02-chaining-commands.jpeg)    
*コマンドを連結して実行*  
  
コマンドは、スラッシュコマンド経由で実行されるスキルです。内容は重なる部分もありますが、保存先が異なります：  
  
- **スキル**: `~/.claude/skills/` - より広いワークフロー定義    
- **コマンド**: `~/.claude/commands/` - すぐ実行できる短いプロンプト  
  
```bash  
# Example skill structure  
~/.claude/skills/  
  pmx-guidelines.md      # Project-specific patterns  
  coding-standards.md    # Language best practices  
  tdd-workflow/          # Multi-file skill with README.md  
  security-review/       # Checklist-based skill  
```  
  
---  
  
## フック（Hooks）  
  
フックは、特定のイベントで発火するトリガーベースの自動化です。スキルと違い、ツール呼び出しやライフサイクルイベントに限定されます。  
  
**フックの種類:**  
1. **PreToolUse** - ツール実行前（検証、リマインド）    
2. **PostToolUse** - ツール実行後（整形、フィードバックループ）    
3. **UserPromptSubmit** - メッセージ送信時    
4. **Stop** - Claude が応答を終えたとき    
5. **PreCompact** - コンテキスト圧縮（compaction）の前    
6. **Notification** - 権限リクエスト  
  
**例：長時間実行コマンドの前に tmux をリマインド**  
  
```json  
{  
  "PreToolUse": [  
    {  
      "matcher": "tool == \"Bash\" && tool_input.command matches \"(npm|pnpm|yarn|cargo|pytest)\"",  
      "hooks": [  
        {  
          "type": "command",  
          "command": "if [ -z \"$TMUX\" ]; then echo '[Hook] Consider tmux for session persistence' >&2; fi"  
        }  
      ]  
    }  
  ]  
}  
```  
  
\!\[PostToolUse hook feedback\] (./assets/images/shortform/03-posttooluse-hook.png)    
*PostToolUse フック実行中に Claude Code で得られるフィードバック例*  
  
**プロのコツ:** JSON を手で書く代わりに `hookify` プラグインを使って会話でフックを作れます。`/hookify` を実行して、やりたいことを説明してください。  
  
---  
  
## サブエージェント（Subagents）  
  
サブエージェントは、オーケストレーター（メインの Claude）が限定スコープでタスクを委譲できるプロセスです。バックグラウンド/フォアグラウンドのどちらでも動かせるため、メインエージェントのコンテキストを節約できます。  
  
サブエージェントはスキルと相性が良いです。スキルの一部を実行できるサブエージェントにタスクを委譲すれば、サブエージェントが自律的にそれらを使って作業できます。また、特定ツール権限でサンドボックス化も可能です。  
  
```bash  
# Example subagent structure  
~/.claude/agents/  
  planner.md           # Feature implementation planning  
  architect.md         # System design decisions  
  tdd-guide.md         # Test-driven development  
  code-reviewer.md     # Quality/security review  
  security-reviewer.md # Vulnerability analysis  
  build-error-resolver.md  
  e2e-runner.md  
  refactor-cleaner.md  
```  
  
適切にスコープを切るために、サブエージェントごとに許可ツール、MCP、権限を設定します。  
  
---  
  
## ルールとメモリ  
  
`.rules` フォルダには、Claude が **常に** 従うべきベストプラクティスを `.md` として置きます。2つのアプローチがあります：  
  
1. **単一の CLAUDE.md** - すべてを1ファイルに（ユーザー/プロジェクトレベル）    
2. **rules フォルダ** - 関心ごとに分割したモジュール構成の `.md`  
  
```bash  
~/.claude/rules/  
  security.md      # No hardcoded secrets, validate inputs  
  coding-style.md  # Immutability, file organization  
  testing.md       # TDD workflow, 80% coverage  
  git-workflow.md  # Commit format, PR process  
  agents.md        # When to delegate to subagents  
  performance.md   # Model selection, context management  
```  
  
**ルール例:**  
- コードベースに絵文字を入れない    
- フロントエンドで紫系の色味は避ける    
- デプロイ前に必ずテストする    
- 巨大ファイルよりモジュール化を優先する    
- console.log をコミットしない    
  
---  
  
## MCP（Model Context Protocol）  
  
MCP は、Claude を外部サービスに直接接続します。API の代替ではなく、プロンプト駆動のラッパーとして機能し、情報のナビゲーションを柔軟にします。  
  
**例:** Supabase MCP により、Claude が特定データを取得したり、SQL を上流で直接実行したりでき、コピペ不要になります。DB やデプロイプラットフォームなども同様です。  
  
\!\[Supabase MCP listing tables\] (./assets/images/shortform/04-supabase-mcp.jpeg)    
*Supabase MCP が public スキーマ内のテーブルを一覧する例*  
  
**Claude 内の Chrome:** ブラウザを Claude が自律操作できる、組み込みプラグイン MCP です。クリックして挙動を確かめたりできます。  
  
**重要：コンテキストウィンドウ管理**    
MCP は厳選してください。私はユーザー設定に MCP を全部入れつつ、**使わないものはすべて無効化** しています。`/plugins` に行って下までスクロールするか、`/mcp` を実行してください。  
  
\!\[/plugins interface\] (./assets/images/shortform/05-plugins-interface.jpeg)    
*/plugins で MCP に移動し、インストール状況とステータスを確認する*  
  
圧縮前の 200k コンテキストでも、ツールを有効にしすぎると 70k まで落ちることがあります。性能は大きく劣化します。  
  
**目安:** 設定上は MCP を 20〜30 個持ちつつ、プロジェクトで有効化は 10 未満 / アクティブツール 80 未満にする。  
  
```bash  
# Check enabled MCPs  
/mcp  
  
# Disable unused ones in ~/.claude.json under projects.disabledMcpServers  
```  
  
---  
  
## プラグイン（Plugins）  
  
プラグインは、面倒な手動セットアップの代わりに、ツールを簡単にインストールできるようパッケージ化します。プラグインは「スキル + MCP」の組み合わせにもなり得ますし、フック/ツールの同梱にもなり得ます。  
  
**プラグインのインストール:**  
  
```bash  
# Add a marketplace  
claude plugin marketplace add https://github.com/mixedbread-ai/mgrep  
  
# Open Claude, run /plugins, find new marketplace, install from there  
```  
  
\!\[Marketplaces tab showing mgrep\] (./assets/images/shortform/06-marketplaces-mgrep.jpeg)    
*新しくインストールされた Mixedbread-Grep マーケットプレイスの表示*  
  
**LSP プラグイン** は、エディタ外で Claude Code を頻繁に使う人に特に有用です。Language Server Protocol により、IDE を開かなくてもリアルタイムの型チェック、定義ジャンプ、賢い補完が可能になります。  
  
```bash  
# Enabled plugins example  
typescript-lsp@claude-plugins-official  # TypeScript intelligence  
pyright-lsp@claude-plugins-official     # Python type checking  
hookify@claude-plugins-official         # Create hooks conversationally  
mgrep@Mixedbread-Grep                   # Better search than ripgrep  
```  
  
MCP と同じ注意：コンテキストウィンドウに気を配ってください。  
  
---  
  
## Tips & Tricks  
  
### キーボードショートカット  
- `Ctrl+U` - 行全体を削除（バックスペース連打より速い）    
- `!` - bash コマンドのクイック接頭辞    
- `@` - ファイル検索    
- `/` - スラッシュコマンドを開始    
- `Shift+Enter` - 複数行入力    
- `Tab` - 思考表示の切替    
- `Esc Esc` - Claude を割り込み / コードを復元    
  
### 並列ワークフロー  
- **Fork**（`/fork`）- キューにメッセージを溜め込む代わりに、重ならないタスクを会話分岐して並列化    
- **Git Worktrees** - 競合なしで「並列 Claude」を回すための方法。各 worktree は独立したチェックアウト  
  
```bash  
git worktree add ../feature-branch feature-branch  
# Now run separate Claude instances in each worktree  
```  
  
### 長時間コマンドには tmux  
Claude が実行するログ/プロセスをストリーミングして監視できます:    
https://github.com/user-attachments/assets/shortform/07-tmux-video.mp4  
  
```bash  
tmux new -s dev  
# Claude runs commands here, you can detach and reattach  
tmux attach -t dev  
```  
  
### mgrep > grep  
`mgrep` は ripgrep/grep を大きく改善します。プラグインマーケットプレイスからインストールし、`/mgrep` スキルを使ってください。ローカル検索と Web 検索の両方に対応します。  
  
```bash  
mgrep "function handleSubmit"  # Local search  
mgrep --web "Next.js 15 app router changes"  # Web search  
```  
  
### その他の便利コマンド  
- `/rewind` - 以前の状態に戻る    
- `/statusline` - ブランチ、コンテキスト%、TODO などをカスタマイズ    
- `/checkpoints` - ファイル単位の復元ポイント    
- `/compact` - 手動でコンテキスト圧縮を実行    
  
### GitHub Actions CI/CD  
GitHub Actions で PR のコードレビューをセットアップできます。設定すれば、Claude が PR を自動レビュー可能です。  
  
\!\[Claude bot approving a PR\] (./assets/images/shortform/08-github-pr-review.jpeg)    
*Claude がバグ修正 PR を承認している例*  
  
### サンドボックス  
危険な操作にはサンドボックスモードを使います。Claude は制限された環境で動作し、実システムへ影響しません。  
  
---  
  
## エディタについて  
  
エディタ選択は Claude Code のワークフローに大きく影響します。Claude Code はどのターミナルからでも動きますが、有能なエディタと組み合わせると、リアルタイムのファイル追跡、素早いナビゲーション、統合されたコマンド実行が可能になります。  
  
### Zed（私の好み）  
私は [Zed](https://zed.dev) を使っています。Rust 製なので本当に速いです。起動が一瞬で、大規模コードベースでも余裕、システムリソースもほとんど使いません。  
  
**Zed + Claude Code が良い理由:**  
- **速度** - Rust ベースの性能により、Claude が高速にファイル編集してもエディタが遅れない    
- **Agent Panel 統合** - Claude の編集に合わせてファイル変更をリアルタイム追跡。参照ファイルへエディタ内で即ジャンプ    
- **CMD+Shift+R コマンドパレット** - カスタムスラッシュコマンド、デバッガ、ビルドスクリプトへ検索 UI で即アクセス    
- **低リソース** - 重い作業中も Claude（特に Opus）と RAM/CPU を奪い合わない    
- **Vim モード** - Vim キーバインドが必要ならフル対応    
  
\!\[Zed Editor with custom commands\] (./assets/images/shortform/09-zed-editor.jpeg)    
*CMD+Shift+R のカスタムコマンドドロップダウンを表示した Zed。右下の照準アイコンがフォロー（Following）モード。*  
  
**エディタ非依存のコツ:**  
1. **画面分割** - 片側に Claude Code のターミナル、もう片側にエディタ    
2. **Ctrl + G** - Zed で Claude が作業中のファイルを素早く開く    
3. **自動保存** - Claude の Read が常に最新になるよう autosave を有効化    
4. **Git 連携** - コミット前にエディタの Git 機能で変更をレビュー    
5. **ファイルウォッチャ** - 多くのエディタは変更ファイルを自動リロード（有効か確認）    
  
### VSCode / Cursor  
こちらも十分に実用的で、Claude Code と相性よく動きます。ターミナル形式で使いつつ `\ide` によりエディタ同期と LSP 機能を有効化できます（プラグインが増えたいまはやや冗長ですが）。また、よりエディタ統合された UI を持つ拡張機能を選ぶこともできます。  
  
\!\[VS Code Claude Code Extension\] (./assets/images/shortform/10-vscode-extension.jpeg)    
*VS Code 拡張は、IDE に直接統合された Claude Code のネイティブ GUI を提供する。*  
  
---  
  
## 私のセットアップ  
  
### プラグイン  
**Installed:**（通常はこのうち 4〜5 個だけ有効化しています）  
  
```markdown  
ralph-wiggum@claude-code-plugins       # Loop automation  
frontend-design@claude-code-plugins    # UI/UX patterns  
commit-commands@claude-code-plugins    # Git workflow  
security-guidance@claude-code-plugins  # Security checks  
pr-review-toolkit@claude-code-plugins  # PR automation  
typescript-lsp@claude-plugins-official # TS intelligence  
hookify@claude-plugins-official        # Hook creation  
code-simplifier@claude-plugins-official  
feature-dev@claude-code-plugins  
explanatory-output-style@claude-code-plugins  
code-review@claude-code-plugins  
context7@claude-plugins-official       # Live documentation  
pyright-lsp@claude-plugins-official    # Python types  
mgrep@Mixedbread-Grep                  # Better search  
```  
  
### MCP サーバー  
**Configured（ユーザーレベル）:**  
  
```json  
{  
  "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"] },  
  "firecrawl": { "command": "npx", "args": ["-y", "firecrawl-mcp"] },  
  "supabase": {  
    "command": "npx",  
    "args": ["-y", "@supabase/mcp-server-supabase@latest", "--project-ref=YOUR_REF"]  
  },  
  "memory": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"] },  
  "sequential-thinking": {  
    "command": "npx",  
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]  
  },  
  "vercel": { "type": "http", "url": "https://mcp.vercel.com" },  
  "railway": { "command": "npx", "args": ["-y", "@railway/mcp-server"] },  
  "cloudflare-docs": { "type": "http", "url": "https://docs.mcp.cloudflare.com/mcp" },  
  "cloudflare-workers-bindings": {  
    "type": "http",  
    "url": "https://bindings.mcp.cloudflare.com/mcp"  
  },  
  "clickhouse": { "type": "http", "url": "https://mcp.clickhouse.cloud/mcp" },  
  "AbletonMCP": { "command": "uvx", "args": ["ableton-mcp"] },  
  "magic": { "command": "npx", "args": ["-y", "@magicuidesign/mcp@latest"] }  
}  
```  
  
ここが重要です。MCP は 14 個設定していますが、プロジェクトごとに有効なのはだいたい 5〜6 個だけ。コンテキストウィンドウを健全に保てます。  
  
### 主要フック  
```json  
{  
  "PreToolUse": [  
    { "matcher": "npm|pnpm|yarn|cargo|pytest", "hooks": ["tmux reminder"] },  
    { "matcher": "Write && .md file", "hooks": ["block unless README/CLAUDE"] },  
    { "matcher": "git push", "hooks": ["open editor for review"] }  
  ],  
  "PostToolUse": [  
    { "matcher": "Edit && .ts/.tsx/.js/.jsx", "hooks": ["prettier --write"] },  
    { "matcher": "Edit && .ts/.tsx", "hooks": ["tsc --noEmit"] },  
    { "matcher": "Edit", "hooks": ["grep console.log warning"] }  
  ],  
  "Stop": [  
    { "matcher": "*", "hooks": ["check modified files for console.log"] }  
  ]  
}  
```  
  
### カスタムステータスライン  
ユーザー、ディレクトリ、（dirty 表示付きの）git ブランチ、残りコンテキスト%、モデル、時刻、TODO 数を表示します:  
  
\!\[Custom status line\] (./assets/images/shortform/11-statusline.jpeg)    
*Mac の root ディレクトリでの statusline 例*  
  
```text  
affoon:~ ctx:65% Opus 4.5 19:52▌▌ plan mode on (shift+tab to cycle)  
```  
  
### ルール構成  
```text  
~/.claude/rules/  
  security.md      # Mandatory security checks  
  coding-style.md  # Immutability, file size limits  
  testing.md       # TDD, 80% coverage  
  git-workflow.md  # Conventional commits  
  agents.md        # Subagent delegation rules  
  patterns.md      # API response formats  
  performance.md   # Model selection (Haiku vs Sonnet vs Opus)  
  hooks.md         # Hook documentation  
```  
  
### サブエージェント  
```text  
~/.claude/agents/  
  planner.md           # Break down features  
  architect.md         # System design  
  tdd-guide.md         # Write tests first  
  code-reviewer.md     # Quality review  
  security-reviewer.md # Vulnerability scan  
  build-error-resolver.md  
  e2e-runner.md        # Playwright tests  
  refactor-cleaner.md  # Dead code removal  
  doc-updater.md       # Keep docs synced  
```  
  
---  
  
## 重要ポイント（Key Takeaways）  
  
1. **ややこしくしすぎない** - 設定はアーキテクチャではなく微調整として扱う    
2. **コンテキストウィンドウは貴重** - 使わない MCP とプラグインは無効化する    
3. **並列実行** - 会話を fork し、git worktrees を使う    
4. **繰り返しを自動化** - 整形、lint、リマインドをフックで    
5. **サブエージェントのスコープを切る** - ツールを絞るほど集中して実行できる    
  
---  
  
## 参考資料  
  
- [Plugins Reference](https://code.claude.com/docs/en/plugins-reference)  
- [Hooks Documentation](https://code.claude.com/docs/en/hooks)  
- [Checkpointing](https://code.claude.com/docs/en/checkpointing)  
- [Interactive Mode](https://code.claude.com/docs/en/interactive-mode)  
- [Memory System](https://code.claude.com/docs/en/memory)  
- [Subagents](https://code.claude.com/docs/en/sub-agents)  
- [MCP Overview](https://code.claude.com/docs/en/mcp-overview)  
  
---  
  
**注:** ここに書いたのは詳細の一部です。高度なパターンは [Longform Guide](./the-longform-guide.md) を参照してください。  
  
---  
  
*NYC で [zenith.chat](https://zenith.chat) を [@DRodriguezFX](https://x.com/DRodriguezFX) と構築して、Anthropic x Forum Ventures ハッカソンで優勝*  