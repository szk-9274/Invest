import buffettPortrait from '../assets/traders/buffett.png'
import dalioPortrait from '../assets/traders/dalio.png'
import lynchPortrait from '../assets/traders/lynch.png'
import minerviniPortrait from '../assets/traders/minervini.png'
import sorosPortrait from '../assets/traders/soros.png'

export type TraderPalette = {
  background: string
  accent: string
  hair: string
  jacket: string
  detail: string
}

type TraderProfileOverride = {
  display_name: string
  short_name: string
  title: string
  description: string
}

type TraderVisual = {
  fallbackPalette: TraderPalette
}

type TraderMetadata = {
  profile: TraderProfileOverride
  visual: TraderVisual
}

const DEFAULT_PALETTE: TraderPalette = {
  background: '#e2e8f0',
  accent: '#64748b',
  hair: '#334155',
  jacket: '#1e293b',
  detail: '#475569',
}

const PORTRAIT_SRC_BY_ASSET_KEY: Record<string, string> = {
  buffett: buffettPortrait,
  dalio: dalioPortrait,
  lynch: lynchPortrait,
  minervini: minerviniPortrait,
  soros: sorosPortrait,
}

const TRADER_METADATA_BY_STRATEGY: Record<string, TraderMetadata> = {
  'buffett-quality': {
    profile: {
      display_name: 'ウォーレン・バフェット',
      short_name: 'ウォーレン・バフェット',
      title: '優良企業の複利成長',
      description: '持続的な競争優位を持つ企業を探します。',
    },
    visual: {
      fallbackPalette: {
        background: '#fef3c7',
        accent: '#f59e0b',
        hair: '#f8fafc',
        jacket: '#1f2937',
        detail: '#92400e',
      },
    },
  },
  'soros-breakout': {
    profile: {
      display_name: 'ジョージ・ソロス',
      short_name: 'ジョージ・ソロス',
      title: '反射性ブレイクアウト・モメンタム',
      description: '力強いブレイクアウトを重視し、勢いが鈍ったら素早く手仕舞います。',
    },
    visual: {
      fallbackPalette: {
        background: '#dbeafe',
        accent: '#2563eb',
        hair: '#cbd5e1',
        jacket: '#0f172a',
        detail: '#1d4ed8',
      },
    },
  },
  'lynch-growth': {
    profile: {
      display_name: 'ピーター・リンチ',
      short_name: 'ピーター・リンチ',
      title: '生活実感に根ざした成長株',
      description: '理解しやすい成長企業を中心に、上昇トレンドの継続性を見極めます。',
    },
    visual: {
      fallbackPalette: {
        background: '#dcfce7',
        accent: '#16a34a',
        hair: '#334155',
        jacket: '#14532d',
        detail: '#166534',
      },
    },
  },
  'minervini-trend': {
    profile: {
      display_name: 'マーク・ミネルヴィニ',
      short_name: 'マーク・ミネルヴィニ',
      title: 'トレンドテンプレート主導',
      description: '52週高値圏の主導株を追い、相対力とブレイクアウトの質を重視します。',
    },
    visual: {
      fallbackPalette: {
        background: '#fae8ff',
        accent: '#c026d3',
        hair: '#0f172a',
        jacket: '#581c87',
        detail: '#a21caf',
      },
    },
  },
  'dalio-balance': {
    profile: {
      display_name: 'レイ・ダリオ',
      short_name: 'レイ・ダリオ',
      title: 'バランス重視のトレンド参加',
      description: '変動を抑えつつトレンドに乗り、持ち過ぎを避けながら安定的な参加を狙います。',
    },
    visual: {
      fallbackPalette: {
        background: '#ede9fe',
        accent: '#7c3aed',
        hair: '#475569',
        jacket: '#312e81',
        detail: '#6d28d9',
      },
    },
  },
}

export function getTraderProfileOverride(strategyName: string) {
  return TRADER_METADATA_BY_STRATEGY[strategyName]?.profile
}

export function getPortraitSrc(assetKey?: string | null) {
  if (!assetKey) return undefined
  return PORTRAIT_SRC_BY_ASSET_KEY[assetKey]
}

export function getTraderVisual(strategyName: string, portraitAssetKey?: string | null) {
  return {
    portraitSrc: getPortraitSrc(portraitAssetKey ?? strategyName),
    fallbackPalette: TRADER_METADATA_BY_STRATEGY[strategyName]?.visual.fallbackPalette ?? DEFAULT_PALETTE,
  }
}

export function isKnownTraderStrategy(strategyName: string) {
  return strategyName in TRADER_METADATA_BY_STRATEGY
}
