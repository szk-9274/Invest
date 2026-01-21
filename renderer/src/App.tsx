import React, { useState, KeyboardEvent } from 'react';
import Titlebar from './components/Titlebar';
import {
  IconHome, IconShield, IconStorage, IconApps, IconToolbox, IconRestore,
  IconSettings, IconFeedback, IconBulb, IconSpark, IconRocket, IconCheckBadge,
  IconCpu, IconBroom, IconPower, IconRefresh
} from './components/Icons';


type NavKey =
  | 'home'
  | 'protect'
  | 'storage'
  | 'apps'
  | 'toolbox'
  | 'restore'
  | 'settings'
  | 'feedback';


export default function App() {
  const nav: { key: NavKey; label: string; icon: React.FC<any> }[] = [
    { key: 'home', label: '初期化', icon: IconHome },
    { key: 'protect', label: 'インテグ', icon: IconShield },
    { key: 'storage', label: '起動確認', icon: IconStorage },
    { key: 'apps', label: 'Teraterm', icon: IconApps },
    { key: 'toolbox', label: 'ネットワーク', icon: IconToolbox },
    { key: 'restore', label: '計測器', icon: IconRestore },
    { key: 'settings', label: 'デバッグ', icon: IconSettings },
  ];


  // 左ナビで選択されたキー
  const [selected, setSelected] = useState<NavKey>('home');


  const handleKey = (e: KeyboardEvent<HTMLDivElement>, key: NavKey) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setSelected(key);
    }
  };


  // ツールボックス用のデモカード（ネットワークタブ）
  const toolCards: { title: string; desc: string; icon: React.FC<any> }[] = [
    { title: '高速化スキャン', desc: '不要な一時データを検出して高速化します', icon: IconRocket },
    { title: 'メモリ最適化', desc: '使用していないメモリを解放します', icon: IconCpu },
    { title: 'ディスククリーン', desc: '一時ファイルやキャッシュをお掃除', icon: IconBroom },
    { title: 'アプリ最適化', desc: 'バックグラウンドの負荷を軽減', icon: IconApps },
    { title: '保護の強化', desc: '安全設定のチェックと推奨事項', icon: IconShield },
  ];

  // インテグ（protect）タブのデモカード
  const integrCards: { title: string; desc: string; icon: React.FC<any> }[] = [
    { title: 'ビルド統合', desc: 'CIパイプラインでビルド・テストを開始します（デモ）', icon: IconShield },
    { title: 'レポート収集', desc: '成果レポートやログの収集を実行します', icon: IconStorage },
    { title: '成果物配置', desc: 'アーティファクトを検証環境へ配置します', icon: IconApps },
    { title: '環境検証', desc: '設定の整合性や権限をチェックします', icon: IconCheckBadge },
  ];

  // 起動確認（storage）タブのデモカード
  const bootCheckCards: { title: string; desc: string; icon: React.FC<any> }[] = [
    { title: '起動時間計測', desc: 'OSと主要プロセスの起動時間を測定', icon: IconPower },
    { title: 'サービス確認', desc: '必須サービスの状態と依存関係をチェック', icon: IconApps },
    { title: 'ログ解析', desc: 'イベントログ・アプリログを簡易解析', icon: IconStorage },
    { title: '自動起動の最適化', desc: 'スタートアップ項目を見直して高速化', icon: IconRocket },
  ];

  // Teraterm（apps）タブのデモカード
  const teratermCards: { title: string; desc: string; icon: React.FC<any> }[] = [
    { title: 'シリアル接続', desc: 'ポート・ボーレートを設定して接続', icon: IconApps },
    { title: 'SSH接続', desc: 'ホスト・鍵認証を設定してログイン', icon: IconShield },
    { title: 'マクロ実行', desc: '事前登録済みのTTlマクロを実行', icon: IconRocket },
    { title: 'ファイル転送', desc: 'ZMODEM/SCPなどで転送を開始', icon: IconStorage },
  ];

  // デバッグ（settings）タブのデモカード
  const debugCards: { title: string; desc: string; icon: React.FC<any> }[] = [
    { title: 'プロセス監視', desc: 'CPU/メモリ使用率を監視（デモ）', icon: IconCpu },
    { title: 'メモリリーク検出', desc: '仮想メモリ/ハンドル数の異常をチェック', icon: IconBroom },
    { title: 'ログレベル切替', desc: 'TRACE/DEBUG/INFOの切替を適用', icon: IconSettings },
    { title: 'ネットワークトレース', desc: '接続/遅延/エラーを簡易トレース', icon: IconToolbox },
  ];


  const renderHome = () => (
    <div className="mx-auto max-w-[900px] space-y-3">
      {/* ヒーロー */}
      <div className="hero p-4">
        <div className="flex items-start gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-full border border-[#30506c] bg-[#1f3346] text-[var(--accent-2)] shadow-inner">
            <IconBulb size={20} />
          </div>
          <div className="min-w-0">
            <div className="text-[14px] font-semibold">Gitlabを活用する</div>
            <div className="mt-1 text-[11px] text-[var(--muted)]">
              サーバ上のメインリポジトリから最新のコミットやブランチを取得します
            </div>
            <div className="mt-1 text-[11px]">
              <span
                className="link cursor-pointer"
                onClick={async () => {
                  try {
                    await window.gitlab.openProjectWeb();
                  } catch (e) {
                    console.error(e);
                    alert('GitLabへの接続に失敗しました。環境変数やネットワーク設定をご確認ください。');
                  }
                }}
              >
                gitlabを見る ›
              </span>
            </div>
          </div>
        </div>
      </div>


      {/* PC ブースト */}
      <div className="card p-4">
        <div className="mb-2 flex items-center justify-between">
          <div className="flex items-center gap-2 font-semibold">
            <div className="badge">
              <IconRocket size={16} />
            </div>
            <span className="text-[14px]">PC ブースト</span>
          </div>
          <button className="text-[11px] link flex items-center gap-1">
            <IconSpark size={16} />
            スマート ブーストをセット
          </button>
        </div>


        <div className="mt-3 grid grid-cols-2 gap-6">
          {/* メモリ使用量 */}
          <div>
            <div className="text-[11px] text-[var(--muted)]">メモリ使用量</div>
            <div className="mt-2 progress-track">
              <div className="progress-fill" style={{ width: '30%' }} />
            </div>
            <div className="mt-2 text-[17px]">30%</div>
          </div>


        {/* 一時ファイル */}
          <div>
            <div className="text-[11px] text-[var(--muted)]">一時ファイル</div>
            <div className="mt-2 progress-track">
              <div className="progress-fill" style={{ width: '5%' }} />
            </div>
            <div className="mt-2 text-[17px]">8KB</div>
          </div>
        </div>


        <button className="btn-boost mt-4 w-full">ブースト</button>
      </div>


      {/* 下のグリッドカード */}
      <div className="grid grid-cols-2 gap-3">
        {/* 正常性チェック */}
        <div className="card p-4">
          <div className="mb-1 flex items-center justify-between">
            <div className="text-[14px] font-semibold">正常性チェック</div>
            <div className="badge">
              <IconCheckBadge size={16} />
            </div>
          </div>
          <div className="text-[11px] text-[var(--muted)]">最終チェック</div>
          <div className="mt-1 text-[16px]">2026/1/9</div>
        </div>


        {/* プロセス */}
        <div className="card p-4">
          <div className="mb-1 flex items-center justify-between">
            <div className="text-[14px] font-semibold">プロセス</div>
            <div className="badge">
              <IconCpu size={16} />
            </div>
          </div>
          <div className="text-[11px] text-[var(--muted)]">処理中</div>
          <div className="mt-1 text-[16px]">17 アプリ</div>
        </div>


        {/* 詳細クリーンアップ */}
        <div className="card p-4">
          <div className="mb-1 flex items-center justify-between">
            <div className="text-[14px] font-semibold">詳細クリーンアップ</div>
            <div className="badge">
              <IconBroom size={16} />
            </div>
          </div>
          <div className="text-[11px] text-[var(--muted)]">Windows (C:)</div>
          <div className="mt-1 text-[16px]">195.7GB/235.5GB</div>
        </div>


        {/* 起動 */}
        <div className="card p-4">
          <div className="mb-1 flex items-center justify-between">
            <div className="text-[14px] font-semibold">起動</div>
            <div className="badge">
              <IconPower size={16} />
            </div>
          </div>
          <div className="text-[11px] text-[var(--muted)]">起動時刻</div>
          <div className="mt-1 text-[16px]">62 秒</div>
        </div>
      </div>
    </div>
  );


  const renderToolbox = () => (
    <div className="mx-auto max-w-[900px] space-y-3">
      {/* ページヘッダー（簡易遷移画面相当） */}
      <div className="hero p-4">
        <div className="flex items-center gap-3">
          <div className="badge">
            <IconToolbox size={16} />
          </div>
          <div>
            <div className="text-[14px] font-semibold">ネットワーク</div>
            <div className="text-[11px] text-[var(--muted)]">
              よく使うメンテナンス機能をまとめています（デモ）
            </div>
          </div>
        </div>
      </div>


      {/* 横長カード 5 個 */}
      <div className="space-y-3">
        {toolCards.map(({ title, desc, icon: Icon }, i) => (
          <div key={i} className="card p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="badge">
                <Icon size={16} />
              </div>
              <div>
                <div className="text-[13px] font-semibold">{title}</div>
                <div className="text-[11px] text-[var(--muted)]">{desc}</div>
              </div>
            </div>
            <button
              className="btn-boost w-[120px]"
              onClick={() => alert(`${title} を実行（デモ）`)}
            >
              ブースト
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderInstruments = () => (
    <div className="mx-auto max-w-[900px] space-y-3">
      {/* 大きめのカードを2つ配置 */}
      <div className="grid grid-cols-1 gap-3">
        {/* 電源（PSU）カード */}
        <div className="card relative p-4">
          {/* 右上リロード */}
          <button
            className="action-btn"
            title="リロード"
            aria-label="PSUリロード"
            onClick={() => alert('PSU 設定のリロード（デモ）')}
          >
            <IconRefresh size={16} />
          </button>

          <div className="mb-2 flex items-center gap-3">
            <div className="badge">
              <IconPower size={16} />
            </div>
            <div>
              <div className="text-[14px] font-semibold">電源（PSU）</div>
              <div className="text-[11px] text-[var(--muted)]">現在値と設定値のモニタ（デモ）</div>
            </div>
          </div>
          {/* 3種類のモニタ値 */}
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2">
              <div className="text-[11px] text-[var(--muted)]">印加電圧</div>
              <div className="mt-1 text-[18px] font-semibold">12.00 V</div>
            </div>
            <div className="rounded border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2">
              <div className="text-[11px] text-[var(--muted)]">印加電流</div>
              <div className="mt-1 text-[18px] font-semibold">0.85 A</div>
            </div>
            <div className="rounded border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2">
              <div className="text-[11px] text-[var(--muted)]">電源設定値</div>
              <div className="mt-1 text-[18px] font-semibold">12.0 V / 1.0 A</div>
            </div>
          </div>
          {/* 操作ボタン（ON/OFFのみ下部に） */}
          <div className="mt-3 flex justify-end gap-2">
            <button
              className="btn-boost w-[88px]"
              onClick={() => alert('PSU 出力 ON（デモ）')}
            >
              ON
            </button>
            <button
              className="btn-boost w-[88px]"
              onClick={() => alert('PSU 出力 OFF（デモ）')}
            >
              OFF
            </button>
          </div>
        </div>

        {/* 恒温槽カード */}
        <div className="card relative p-4">
          {/* 右上リロード */}
          <button
            className="action-btn"
            title="リロード"
            aria-label="恒温槽リロード"
            onClick={() => alert('恒温槽 設定のリロード（デモ）')}
          >
            <IconRefresh size={16} />
          </button>

          <div className="mb-2 flex items-center gap-3">
            <div className="badge">
              <IconSpark size={16} />
            </div>
            <div>
              <div className="text-[14px] font-semibold">恒温槽</div>
              <div className="text-[11px] text-[var(--muted)]">温度/湿度/設定値のモニタ（デモ）</div>
            </div>
          </div>
          {/* 3種類のモニタ値 */}
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2">
              <div className="text-[11px] text-[var(--muted)]">現在温度</div>
              <div className="mt-1 text-[18px] font-semibold">23.5 ℃</div>
            </div>
            <div className="rounded border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2">
              <div className="text-[11px] text-[var(--muted)]">現在湿度</div>
              <div className="mt-1 text-[18px] font-semibold">45 %</div>
            </div>
            <div className="rounded border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2">
              <div className="text-[11px] text-[var(--muted)]">温度設定</div>
              <div className="mt-1 text-[18px] font-semibold">25.0 ℃</div>
            </div>
          </div>
          {/* 操作ボタン */}
          <div className="mt-3 flex justify-end gap-2">
            <button
              className="btn-boost w-[88px]"
              onClick={() => alert('恒温槽 低温に設定（デモ）')}
            >
              低温
            </button>
            <button
              className="btn-boost w-[88px]"
              onClick={() => alert('恒温槽 常温に設定（デモ）')}
            >
              常温
            </button>
            <button
              className="btn-boost w-[88px]"
              onClick={() => alert('恒温槽 高温に設定（デモ）')}
            >
              高温
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderIntegr = () => (
    <div className="mx-auto max-w-[900px] space-y-3">
      <div className="hero p-4">
        <div className="flex items-center gap-3">
          <div className="badge">
            <IconShield size={16} />
          </div>
          <div>
            <div className="text-[14px] font-semibold">インテグ</div>
            <div className="text-[11px] text-[var(--muted)]">
              ビルド/成果物/環境の統合系タスク（デモ）
            </div>
          </div>
        </div>
      </div>
      <div className="space-y-3">
        {integrCards.map(({ title, desc, icon: Icon }, i) => (
          <div key={i} className="card p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="badge"><Icon size={16} /></div>
              <div>
                <div className="text-[13px] font-semibold">{title}</div>
                <div className="text-[11px] text-[var(--muted)]">{desc}</div>
              </div>
            </div>
            <button
              className="btn-boost w-[120px]"
              onClick={() => alert(`${title} を実行（デモ）`)}
            >実行</button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderBootCheck = () => (
    <div className="mx-auto max-w-[900px] space-y-3">
      <div className="hero p-4">
        <div className="flex items-center gap-3">
          <div className="badge">
            <IconStorage size={16} />
          </div>
          <div>
            <div className="text-[14px] font-semibold">起動確認</div>
            <div className="text-[11px] text-[var(--muted)]">
              起動時間やサービス・ログを確認（デモ）
            </div>
          </div>
        </div>
      </div>
      <div className="space-y-3">
        {bootCheckCards.map(({ title, desc, icon: Icon }, i) => (
          <div key={i} className="card p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="badge"><Icon size={16} /></div>
              <div>
                <div className="text-[13px] font-semibold">{title}</div>
                <div className="text-[11px] text-[var(--muted)]">{desc}</div>
              </div>
            </div>
            <button
              className="btn-boost w-[120px]"
              onClick={() => alert(`${title} を実行（デモ）`)}
            >実行</button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTeraterm = () => (
    <div className="mx-auto max-w-[900px] space-y-3">
      <div className="hero p-4">
        <div className="flex items-center gap-3">
          <div className="badge">
            <IconApps size={16} />
          </div>
          <div>
            <div className="text-[14px] font-semibold">Teraterm</div>
            <div className="text-[11px] text-[var(--muted)]">
              接続/マクロ/転送などの操作（デモ）
            </div>
          </div>
        </div>
      </div>
      <div className="space-y-3">
        {teratermCards.map(({ title, desc, icon: Icon }, i) => (
          <div key={i} className="card p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="badge"><Icon size={16} /></div>
              <div>
                <div className="text-[13px] font-semibold">{title}</div>
                <div className="text-[11px] text-[var(--muted)]">{desc}</div>
              </div>
            </div>
            <button
              className="btn-boost w-[120px]"
              onClick={() => alert(`${title} を実行（デモ）`)}
            >実行</button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDebug = () => (
    <div className="mx-auto max-w-[900px] space-y-3">
      <div className="hero p-4">
        <div className="flex items-center gap-3">
          <div className="badge">
            <IconSettings size={16} />
          </div>
          <div>
            <div className="text-[14px] font-semibold">デバッグ</div>
            <div className="text-[11px] text-[var(--muted)]">
              監視・設定・トレースの支援（デモ）
            </div>
          </div>
        </div>
      </div>
      <div className="space-y-3">
        {debugCards.map(({ title, desc, icon: Icon }, i) => (
          <div key={i} className="card p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="badge"><Icon size={16} /></div>
              <div>
                <div className="text-[13px] font-semibold">{title}</div>
                <div className="text-[11px] text-[var(--muted)]">{desc}</div>
              </div>
            </div>
            <button
              className="btn-boost w-[120px]"
              onClick={() => alert(`${title} を実行（デモ）`)}
            >実行</button>
          </div>
        ))}
      </div>
    </div>
  );


  const renderContent = () => {
    if (selected === 'home') return renderHome();
    if (selected === 'toolbox') return renderToolbox();
    if (selected === 'restore') return renderInstruments();
    if (selected === 'protect') return renderIntegr();
    if (selected === 'storage') return renderBootCheck();
    if (selected === 'apps') return renderTeraterm();
    if (selected === 'settings') return renderDebug();
    // その他のページは一旦空
    return <div className="h-full" />;
  };


  return (
    <div className="h-full">
      <Titlebar />


      <div className="flex h-[calc(100%-36px)]">
        {/* サイドレール */}
        <aside className="relative w-[86px] border-r border-[var(--border)] bg-[var(--rail)] pt-3">
          <div className="flex flex-col items-center gap-5">
            {nav.map(({ key, label, icon: Icon }) => {
              const active = key === selected;
              return (
                <div key={key} className="relative">
                  {active && <div className="nav-accent" />}
                  <div
                    role="button"
                    tabIndex={0}
                    aria-current={active ? 'page' : undefined}
                    title={label}
                    className={`nav-item ${active ? 'active' : ''}`}
                    onClick={() => setSelected(key)}
                    onKeyDown={(e) => handleKey(e, key)}
                  >
                    <Icon size={26} />
                    <div className="label">{label}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>


        {/* メインコンテンツ */}
        <main className="flex-1 bg-[var(--panel)] p-4 overflow-hidden">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
