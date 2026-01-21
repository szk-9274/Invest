import React from 'react';
import { LogoGlyph } from './Icons';

export default function Titlebar() {
  return (
    <div className="titlebar flex h-9 items-center justify-between px-2">
      <div className="flex items-center gap-2">
        <div className="no-drag">
          <LogoGlyph size={16} />
        </div>
        <div className="select-none text-[13px] tracking-wide text-[var(--text)]">Microsoft PC Manager</div>
      </div>

    <div className="no-drag flex items-center">
      <button
        onClick={() => window.win.minimize()}
        className="grid h-8 w-10 place-items-center rounded hover:bg-[#1a2a39]"
        title="最小化"
        aria-label="最小化"
      >
        <span className="mt-[3px] text-[12px] leading-none">—</span>
      </button>
      <button
        onClick={() => window.win.close()}
        className="grid h-8 w-10 place-items-center rounded hover:bg-[#e81123]"
        title="閉じる"
        aria-label="閉じる"
      >
        <span className="text-[22px] leading-none">×</span>
      </button>
    </div>
  </div>
  );
}