import React from 'react'

type TraderAvatarProps = {
  traderKey: string
  label: string
}

type TraderPalette = {
  background: string
  accent: string
  hair: string
  jacket: string
  detail: string
}

const PALETTE_BY_TRADER: Record<string, TraderPalette> = {
  'buffett-quality': {
    background: '#fef3c7',
    accent: '#f59e0b',
    hair: '#f8fafc',
    jacket: '#1f2937',
    detail: '#92400e',
  },
  'soros-breakout': {
    background: '#dbeafe',
    accent: '#2563eb',
    hair: '#cbd5e1',
    jacket: '#0f172a',
    detail: '#1d4ed8',
  },
  'lynch-growth': {
    background: '#dcfce7',
    accent: '#16a34a',
    hair: '#334155',
    jacket: '#14532d',
    detail: '#166534',
  },
  'minervini-trend': {
    background: '#fae8ff',
    accent: '#c026d3',
    hair: '#0f172a',
    jacket: '#581c87',
    detail: '#a21caf',
  },
  'dalio-balance': {
    background: '#ede9fe',
    accent: '#7c3aed',
    hair: '#475569',
    jacket: '#312e81',
    detail: '#6d28d9',
  },
}

const DEFAULT_PALETTE: TraderPalette = {
  background: '#e2e8f0',
  accent: '#64748b',
  hair: '#334155',
  jacket: '#1e293b',
  detail: '#475569',
}

export const TraderAvatar: React.FC<TraderAvatarProps> = ({ traderKey, label }) => {
  const palette = PALETTE_BY_TRADER[traderKey] ?? DEFAULT_PALETTE

  return (
    <span className="trader-avatar" aria-hidden="true">
      <svg viewBox="0 0 80 80" role="img" aria-label={`${label} アバター`}>
        <circle cx="40" cy="40" r="38" fill={palette.background} />
        <circle cx="40" cy="32" r="18" fill="#f8d4b4" />
        <path d="M22 28c2-10 10-16 18-16s16 6 18 16c-4-3-9-5-18-5s-14 2-18 5Z" fill={palette.hair} />
        <ellipse cx="34" cy="34" rx="2.4" ry="2.8" fill="#1f2937" />
        <ellipse cx="46" cy="34" rx="2.4" ry="2.8" fill="#1f2937" />
        <path d="M34 44c3.5 3 8.5 3 12 0" fill="none" stroke={palette.detail} strokeWidth="3" strokeLinecap="round" />
        <path d="M20 72c2-16 12-24 20-24s18 8 20 24" fill={palette.jacket} />
        <path d="M40 48l-6 10h12l-6-10Z" fill={palette.accent} />
        <circle cx="18" cy="18" r="5" fill={palette.accent} opacity="0.85" />
        <circle cx="62" cy="18" r="4" fill={palette.detail} opacity="0.65" />
      </svg>
    </span>
  )
}
