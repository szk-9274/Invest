---**言語:** English | [繁體中文](docs/zh-TW/README.md)  
  
# Everything Claude Code  
  
[\!\[Stars\] (https://img.shields.io/github/stars/affaan-m/everything-claude-code?style=flat)](https://github.com/affaan-m/everything-claude-code/stargazers)[\!\[License\] (https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)\!\[Shell\] (https://img.shields.io/badge/-Shell-4EAA25?logo=gnu-bash&logoColor=white)\!\[TypeScript\] (https://img.shields.io/badge/-TypeScript-3178C6?logo=typescript&logoColor=white)\!\[Go\] (https://img.shields.io/badge/-Go-00ADD8?logo=go&logoColor=white)\!\[Markdown\] (https://img.shields.io/badge/-Markdown-000000?logo=markdown&logoColor=white)  
  
---  
  
<div align="center">  
    
**🌐 Language / 语言 / 語言**    
[**English**](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](docs/zh-TW/README.md)  
  
</div>  
  
---  
  
**Anthropic ハッカソン優勝者による、Claude Code 設定の完全コレクション。**    
実プロダクトを作りながら、10か月以上にわたる集中的な日次利用で進化してきた、本番対応のエージェント、スキル、フック、コマンド、ルール、MCP 設定を収録。  
  
---  
  
## ガイド  
  
このリポジトリは「生のコードのみ」です。すべての解説はガイドにあります。  
  
<table>  
  <tr>  
    <td width="50%">  
      <a href="https://x.com/affaanmustafa/status/2012378465664745795">  
        <img src="https://github.com/user-attachments/assets/1a471488-59cc-425b-8345-5245c7efbcef" alt="The Shorthand Guide to Everything Claude Code" />  
      </a>  
    </td>  
    <td width="50%">  
      <a href="https://x.com/affaanmustafa/status/2014040193557471352">  
        <img src="https://github.com/user-attachments/assets/c9ca43bc-b149-427f-b551-af6840c368f0" alt="The Longform Guide to Everything Claude Code" />  
      </a>  
    </td>  
  </tr>  
  <tr>  
    <td align="center">  
      <b>Shorthand Guide</b><br/>  
      セットアップ、基礎、思想。<b>まずはこちらを読む。</b>  
    </td>  
    <td align="center">  
      <b>Longform Guide</b><br/>  
      トークン最適化、メモリ永続化、評価（evals）、並列化。  
    </td>  
  </tr>  
</table>  
  
| トピック | 学べること |  
|-------|-------------------|  
| トークン最適化 | モデル選定、システムプロンプトのスリム化、バックグラウンド処理 |  
| メモリ永続化 | セッションをまたいで自動的にコンテキストを保存/読込するフック |  
| 継続学習 | セッションからパターンを自動抽出して再利用可能なスキルへ |  
| 検証ループ | チェックポイント vs 継続 eval、採点者タイプ、pass@k 指標 |  
| 並列化 | Git worktrees、カスケード手法、インスタンスをスケールするタイミング |  
| サブエージェントのオーケストレーション | コンテキスト問題、反復的リトリーバル（iterative retrieval）パターン |  
  
---  
  
## 🚀 クイックスタート  
  
2分以内に使い始める:  
  
### Step 1: プラグインをインストール  
  
```bash  
# Add marketplace/plugin  
plugin marketplace add affaan-m/everything-claude-code  
  
# Install plugin  
plugin install everything-claude-code@everything-claude-code  
```  
  
### Step 2: ルールをインストール（必須）  
  
> ⚠️ **重要:** Claude Code のプラグインは `rules` を自動配布できません。手動でインストールしてください。  
  
```bash  
# Clone the repo first  
git clone https://github.com/affaan-m/everything-claude-code.git  
  
# Copy rules (applies to all projects)  
cp -r everything-claude-code/rules/* ~/.claude/rules/  
```  
  
### Step 3: 使い始める  
  
```bash  
# Try a command  
/plan "Add user authentication"  
  
# Check available commands  
/plugin list everything-claude-code@everything-claude-code  
```  
  
✨ **これで完了!** 15以上のエージェント、30以上のスキル、20以上のコマンドにアクセスできます。  
  
---  
  
## 🌐 クロスプラットフォーム対応  
  
このプラグインは現在 **Windows / macOS / Linux** を完全サポートします。互換性最大化のため、すべてのフックとスクリプトを Node.js で書き直しました。  
  
### パッケージマネージャ検出  
  
プラグインは、次の優先順位で希望のパッケージマネージャ（npm / pnpm / yarn / bun）を自動検出します:  
  
1. **環境変数**: `CLAUDE_PACKAGE_MANAGER`    
2. **プロジェクト設定**: `.claude/package-manager.json`    
3. **package.json**: `packageManager` フィールド    
4. **ロックファイル**: package-lock.json / yarn.lock / pnpm-lock.yaml / bun.lockb の検出    
5. **グローバル設定**: `~/.claude/package-manager.json`    
6. **フォールバック**: 利用可能なパッケージマネージャの先頭  
  
希望のパッケージマネージャを設定するには:  
  
```bash  
# Via environment variable  
export CLAUDE_PACKAGE_MANAGER=pnpm  
  
# Via global config  
node scripts/setup-package-manager.js --global pnpm  
  
# Via project config  
node scripts/setup-package-manager.js --project bun  
  
# Detect current setting  
node scripts/setup-package-manager.js --detect  
```  
  
または、Claude Code で `/setup-pm` コマンドを使用します。  
  
---  
  
## 📦 収録内容  
  
このリポジトリは **Claude Code プラグイン** です。直接インストールするか、必要なコンポーネントだけを手動でコピーできます。  
  
```text  
everything-claude-code/  
|-- .claude-plugin/   # プラグインとマーケットプレイスのマニフェスト  
|   |-- plugin.json         # プラグインのメタデータとコンポーネントパス  
|   |-- marketplace.json    # /plugin marketplace add 用のマーケットプレイスカタログ  
|  
|-- agents/           # 委譲用の特化サブエージェント  
|   |-- planner.md           # 機能実装の計画  
|   |-- architect.md         # システム設計の意思決定  
|   |-- tdd-guide.md         # テスト駆動開発  
|   |-- code-reviewer.md     # 品質/セキュリティレビュー  
|   |-- security-reviewer.md # 脆弱性分析  
|   |-- build-error-resolver.md  
|   |-- e2e-runner.md        # Playwright E2E テスト  
|   |-- refactor-cleaner.md  # デッドコード掃除  
|   |-- doc-updater.md       # ドキュメント同期  
|   |-- go-reviewer.md       # Go コードレビュー (NEW)  
|   |-- go-build-resolver.md # Go ビルドエラー解決 (NEW)  
|  
|-- skills/           # ワークフロー定義とドメイン知識  
|   |-- coding-standards/           # 言語別ベストプラクティス  
|   |-- backend-patterns/           # API/DB/キャッシュのパターン  
|   |-- frontend-patterns/          # React/Next.js パターン  
|   |-- continuous-learning/        # セッションから自動抽出 (Longform Guide)  
|   |-- continuous-learning-v2/     # 信頼度スコア付きの本能（instinct）ベース学習  
|   |-- iterative-retrieval/        # サブエージェント向け段階的コンテキスト洗練  
|   |-- strategic-compact/          # 手動コンパクション提案 (Longform Guide)  
|   |-- tdd-workflow/               # TDD 手法  
|   |-- security-review/            # セキュリティチェックリスト  
|   |-- eval-harness/               # 検証ループ評価 (Longform Guide)  
|   |-- verification-loop/          # 継続検証 (Longform Guide)  
|   |-- golang-patterns/            # Go のイディオム/ベストプラクティス (NEW)  
|   |-- golang-testing/             # Go テストパターン/TDD/ベンチマーク (NEW)  
|  
|-- commands/         # すぐ実行できるスラッシュコマンド  
|   |-- tdd.md              # /tdd - テスト駆動開発  
|   |-- plan.md             # /plan - 実装計画  
|   |-- e2e.md              # /e2e - E2E テスト生成  
|   |-- code-review.md      # /code-review - 品質レビュー  
|   |-- build-fix.md        # /build-fix - ビルドエラー修正  
|   |-- refactor-clean.md   # /refactor-clean - デッドコード削除  
|   |-- learn.md            # /learn - セッション途中でパターン抽出 (Longform Guide)  
|   |-- checkpoint.md       # /checkpoint - 検証状態を保存 (Longform Guide)  
|   |-- verify.md           # /verify - 検証ループ実行 (Longform Guide)  
|   |-- setup-pm.md         # /setup-pm - パッケージマネージャ設定  
|   |-- go-review.md        # /go-review - Go コードレビュー (NEW)  
|   |-- go-test.md          # /go-test - Go TDD ワークフロー (NEW)  
|   |-- go-build.md         # /go-build - Go ビルドエラー修正 (NEW)  
|   |-- skill-create.md     # /skill-create - git 履歴からスキル生成 (NEW)  
|   |-- instinct-status.md  # /instinct-status - 学習済み本能を表示 (NEW)  
|   |-- instinct-import.md  # /instinct-import - 本能をインポート (NEW)  
|   |-- instinct-export.md  # /instinct-export - 本能をエクスポート (NEW)  
|   |-- evolve.md           # /evolve - 本能をクラスタリングしてスキル化 (NEW)  
|  
|-- rules/            # 常に守るガイドライン（~/.claude/rules/ にコピー）  
|   |-- security.md         # 必須セキュリティチェック  
|   |-- coding-style.md     # 不変性、ファイル構成  
|   |-- testing.md          # TDD、カバレッジ 80% 要件  
|   |-- git-workflow.md     # コミット形式、PR プロセス  
|   |-- agents.md           # サブエージェントへ委譲するタイミング  
|   |-- performance.md      # モデル選定、コンテキスト管理  
|  
|-- hooks/            # トリガーベースの自動化  
|   |-- hooks.json                # すべてのフック設定（PreToolUse / PostToolUse / Stop など）  
|   |-- memory-persistence/       # セッションライフサイクルフック (Longform Guide)  
|   |-- strategic-compact/        # コンパクション提案 (Longform Guide)  
|  
|-- scripts/          # クロスプラットフォーム Node.js スクリプト (NEW)  
|   |-- lib/                     # 共通ユーティリティ  
|   |   |-- utils.js             # クロスプラットフォームのファイル/パス/システムユーティリティ  
|   |   |-- package-manager.js   # パッケージマネージャの検出と選択  
|   |-- hooks/                   # フック実装  
|   |   |-- session-start.js     # セッション開始時にコンテキスト読込  
|   |   |-- session-end.js       # セッション終了時に状態保存  
|   |   |-- pre-compact.js       # コンパクション前の状態保存  
|   |   |-- suggest-compact.js   # 戦略的コンパクション提案  
|   |   |-- evaluate-session.js  # セッションからパターン抽出  
|   |-- setup-package-manager.js # 対話式 PM セットアップ  
|  
|-- tests/            # テストスイート (NEW)  
|   |-- lib/                     # ライブラリテスト  
|   |-- hooks/                   # フックテスト  
|   |-- run-all.js               # 全テスト実行  
|  
|-- contexts/         # 動的な system prompt 注入コンテキスト (Longform Guide)  
|   |-- dev.md              # 開発モードコンテキスト  
|   |-- review.md           # コードレビューモードコンテキスト  
|   |-- research.md         # 調査/探索モードコンテキスト  
|  
|-- examples/         # 設定とセッションの例  
|   |-- CLAUDE.md           # プロジェクトレベル設定の例  
|   |-- user-CLAUDE.md      # ユーザーレベル設定の例  
|  
|-- mcp-configs/      # MCP サーバー設定  
|   |-- mcp-servers.json    # GitHub, Supabase, Vercel, Railway など  
|  
|-- marketplace.json  # セルフホスト型マーケットプレイス設定（/plugin marketplace add 用）  
```  
  
---  
  
## 🛠️ エコシステムツール  
  
### Skill Creator  
  
リポジトリから Claude Code のスキルを生成する方法は2つあります:  
  
#### Option A: ローカル解析（内蔵）  
  
外部サービス不要で、ローカル解析を行う `/skill-create` コマンドを使います:  
  
```bash  
/skill-create                    # Analyze current repo  
/skill-create --instincts        # Also generate instincts for continuous-learning  
```  
  
git 履歴をローカルに解析し、SKILL.md ファイルを生成します。  
  
#### Option B: GitHub App（上級）  
  
高度な機能（1万+コミット、PR 自動作成、チーム共有など）が必要なら:  
  
[Install GitHub App](https://github.com/apps/skill-creator) | [ecc.tools](https://ecc.tools)  
  
```bash  
# Comment on any issue:  
 /skill-creator analyze  
  
# Or auto-triggers on push to default branch  
```  
  
どちらの方法でも次が作られます:  
- **SKILL.md ファイル** - Claude Code ですぐ使えるスキル  
- **Instinct コレクション** - continuous-learning-v2 用  
- **パターン抽出** - コミット履歴から学習  
  
### 🧠 Continuous Learning v2  
  
本能（instinct）ベースの学習システムが、あなたのパターンを自動学習します:  
  
```bash  
/instinct-status        # Show learned instincts with confidence  
/instinct-import <file> # Import instincts from others  
/instinct-export        # Export your instincts for sharing  
/evolve                 # Cluster related instincts into skills  
```  
  
詳細ドキュメントは `skills/continuous-learning-v2/` を参照してください。  
  
---  
  
## 📋 要件  
  
### Claude Code CLI バージョン  
  
**最低バージョン: v2.1.0 以降**  
  
このプラグインは、プラグインシステムのフック取り扱い変更により Claude Code CLI v2.1.0+ が必要です。  
  
バージョン確認:  
  
```bash  
claude --version  
```  
  
### 重要: フックの自動ロード挙動  
  
> ⚠️ **コントリビューター向け:** `.claude-plugin/plugin.json` に `"hooks"` フィールドを追加しないでください。これは回帰テストで強制されています。  
  
Claude Code v2.1+ は慣例により、インストール済みプラグインから `hooks/hooks.json` を **自動的にロード** します。`plugin.json` に明示すると重複検出エラーになります:  
  
```text  
Duplicate hooks file detected: ./hooks/hooks.json resolves to already-loaded file  
```  
  
**経緯:** この挙動は本リポジトリで繰り返し fix/revert を引き起こしてきました（[#29](https://github.com/affaan-m/everything-claude-code/issues/29), [#52](https://github.com/affaan-m/everything-claude-code/issues/52), [#103](https://github.com/affaan-m/everything-claude-code/issues/103)）。Claude Code のバージョン間で挙動が変わったため混乱が生じました。現在は回帰テストで再導入を防いでいます。  
  
---  
  
## 📥 インストール  
  
### Option 1: プラグインとしてインストール（推奨）  
  
このリポジトリを使う最も簡単な方法は、Claude Code プラグインとしてインストールすることです:  
  
```bash  
# Add this repo as a marketplace  
plugin marketplace add affaan-m/everything-claude-code  
  
# Install the plugin  
plugin install everything-claude-code@everything-claude-code  
```  
  
または `~/.claude/settings.json` に直接追加します:  
  
```json  
{  
  "extraKnownMarketplaces": {  
    "everything-claude-code": {  
      "source": {  
        "source": "github",  
        "repo": "affaan-m/everything-claude-code"  
      }  
    }  
  },  
  "enabledPlugins": {  
    "everything-claude-code@everything-claude-code": true  
  }  
}  
```  
  
これで、すべてのコマンド、エージェント、スキル、フックに即座にアクセスできます。  
  
> **注:** Claude Code のプラグインシステムは、プラグイン経由で `rules` を配布できません（[上流の制限](https://code.claude.com/docs/en/plugins-reference)）。ルールは手動でインストールしてください:    
>  
> ```bash  
> # Clone the repo first  
> git clone https://github.com/affaan-m/everything-claude-code.git  
>  
> # Option A: User-level rules (applies to all projects)  
> cp -r everything-claude-code/rules/* ~/.claude/rules/  
>  
> # Option B: Project-level rules (applies to current project only)  
> mkdir -p .claude/rules  
> cp -r everything-claude-code/rules/* .claude/rules/  
> ```  
  
---  
  
### 🔧 Option 2: 手動インストール  
  
インストール内容を手動で制御したい場合:  
  
```bash  
# Clone the repo  
git clone https://github.com/affaan-m/everything-claude-code.git  
  
# Copy agents to your Claude config  
cp everything-claude-code/agents/*.md ~/.claude/agents/  
  
# Copy rules  
cp everything-claude-code/rules/*.md ~/.claude/rules/  
  
# Copy commands  
cp everything-claude-code/commands/*.md ~/.claude/commands/  
  
# Copy skills  
cp -r everything-claude-code/skills/* ~/.claude/skills/  
```  
  
#### hooks を settings.json に追加  
  
`hooks/hooks.json` からフックを `~/.claude/settings.json` にコピーしてください。  
  
#### MCP を設定  
  
`mcp-configs/mcp-servers.json` から必要な MCP サーバーを `~/.claude.json` にコピーしてください。  
  
**重要:** `YOUR_*_HERE` プレースホルダを実際の API キーに置き換えてください。  
  
---  
  
## 🎯 重要コンセプト  
  
### Agents（エージェント）  
  
サブエージェントは、限定されたスコープで委譲タスクを処理します。例:  
  
```markdown  
---  
name: code-reviewer  
description: Reviews code for quality, security, and maintainability  
tools: ["Read", "Grep", "Glob", "Bash"]  
model: opus  
---  
  
You are a senior code reviewer...  
```  
  
### Skills（スキル）  
  
スキルは、コマンドやエージェントから呼び出されるワークフロー定義です:  
  
```markdown  
# TDD Workflow  
1. Define interfaces first  
2. Write failing tests (RED)  
3. Implement minimal code (GREEN)  
4. Refactor (IMPROVE)  
5. Verify 80%+ coverage  
```  
  
### Hooks（フック）  
  
フックはツールイベントで発火します。例: console.log を警告する:  
  
```json  
{  
  "matcher": "tool == \"Edit\" && tool_input.file_path matches \"\\\\.(ts|tsx|js|jsx)$\"",  
  "hooks": [{  
    "type": "command",  
    "command": "#!/bin/bash\ngrep -n 'console\\.log' \"$file_path\" && echo '[Hook] Remove console.log' >&2"  
  }]  
}  
```  
  
### Rules（ルール）  
  
ルールは常時適用されるガイドラインです。モジュール化しておきましょう:  
  
```text  
~/.claude/rules/  
  security.md      # シークレットのハードコード禁止  
  coding-style.md  # 不変性、ファイル制限  
  testing.md       # TDD、カバレッジ要件  
```  
  
---  
  
## 🧪 テストの実行  
  
このプラグインには包括的なテストスイートが含まれます:  
  
```bash  
# Run all tests  
node tests/run-all.js  
  
# Run individual test files  
node tests/lib/utils.test.js  
node tests/lib/package-manager.test.js  
node tests/hooks/hooks.test.js  
```  
  
---  
  
## 🤝 コントリビュート  
  
**コントリビュートは歓迎・推奨です。**    
このリポジトリはコミュニティリソースとして作られています。以下があればぜひ:  
  
- 便利なエージェントやスキル  
- 気の利いたフック  
- より良い MCP 設定  
- 改善されたルール  
  
ガイドラインは [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。  
  
### コントリビュート案  
  
- 言語別スキル（Python / Rust パターン）- Go は追加済み!  
- フレームワーク別設定（Django / Rails / Laravel）  
- DevOps エージェント（Kubernetes / Terraform / AWS）  
- テスト戦略（各種フレームワーク）  
- ドメイン特化知識（ML / データエンジニアリング / モバイル）  
  
---  
  
## 📖 背景  
  
実験的ロールアウト以来、Claude Code を使い続けています。2025年9月に Anthropic x Forum Ventures ハッカソンで、[@DRodriguezFX](https://x.com/DRodriguezFX) と一緒に [zenith.chat](https://zenith.chat) を構築して優勝しました（完全に Claude Code を使用）。  
  
これらの設定は、複数の本番アプリケーションで鍛えられています。  
  
---  
  
## ⚠️ 重要な注意事項  
  
### コンテキストウィンドウ管理  
  
**重要:** すべての MCP を一度に有効化しないでください。ツールを有効にしすぎると、200k のコンテキストウィンドウが 70k まで縮むことがあります。  
  
目安:  
- MCP は 20〜30 個設定しておく  
- 1プロジェクトで有効化は 10 個未満に抑える  
- アクティブなツールは 80 未満  
  
プロジェクト設定の `disabledMcpServers` を使って不要なものを無効化してください。  
  
### カスタマイズ  
  
これらの設定は私のワークフローに最適化されています。あなたは次を行うべきです:  
1. しっくりくるものから始める  
2. 自分のスタックに合わせて変更する  
3. 使わないものは削除する  
4. 自分のパターンを追加する  
  
---  
  
## 🌟 Star History  
  
[\!\[Star History Chart\] (https://api.star-history.com/svg?repos=affaan-m/everything-claude-code&type=Date)](https://star-history.com/#affaan-m/everything-claude-code&Date)  
  
---  
  
## 🔗 リンク  
  
- **Shorthand Guide（まずはこちら）:** [The Shorthand Guide to Everything Claude Code](https://x.com/affaanmustafa/status/2012378465664745795)  
- **Longform Guide（上級）:** [The Longform Guide to Everything Claude Code](https://x.com/affaanmustafa/status/2014040193557471352)  
- **Follow:** [@affaanmustafa](https://x.com/affaanmustafa)  
- **zenith.chat:** [zenith.chat](https://zenith.chat)  
  
---  
  
## 📄 ライセンス  
  
MIT - 自由に利用・必要に応じて改変・可能なら貢献の還元も歓迎。  
  
---  
  
**役に立ったらこのリポジトリに Star を。両方のガイドを読んで、素晴らしいものを作ろう。**  