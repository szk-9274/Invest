import type { StrategyProfile } from '../api/backtest'

type StrategyProfileOverride = Pick<StrategyProfile, 'display_name' | 'short_name' | 'title' | 'description'>

const COPY_BY_STRATEGY: Record<string, StrategyProfileOverride> = {
  'rule-based-stage2': {
    display_name: 'ベースライン Stage2',
    short_name: 'ベースライン',
    title: 'Stage2 トレンド基準戦略',
    description: '比較の基準に使う Stage2 の標準戦略です。',
  },
  'buffett-quality': {
    display_name: 'ウォーレン・バフェット',
    short_name: 'ウォーレン・バフェット',
    title: '優良企業の複利成長',
    description: '持続的な競争優位を持つ企業を探します。',
  },
  'soros-breakout': {
    display_name: 'ジョージ・ソロス',
    short_name: 'ジョージ・ソロス',
    title: '反射性ブレイクアウト・モメンタム',
    description: '力強いブレイクアウトを重視し、勢いが鈍ったら素早く手仕舞います。',
  },
  'lynch-growth': {
    display_name: 'ピーター・リンチ',
    short_name: 'ピーター・リンチ',
    title: '生活実感に根ざした成長株',
    description: '理解しやすい成長企業を中心に、上昇トレンドの継続性を見極めます。',
  },
  'minervini-trend': {
    display_name: 'マーク・ミネルヴィニ',
    short_name: 'マーク・ミネルヴィニ',
    title: 'トレンドテンプレート主導',
    description: '52週高値圏の主導株を追い、相対力とブレイクアウトの質を重視します。',
  },
  'dalio-balance': {
    display_name: 'レイ・ダリオ',
    short_name: 'レイ・ダリオ',
    title: 'バランス重視のトレンド参加',
    description: '変動を抑えつつトレンドに乗り、持ち過ぎを避けながら安定的な参加を狙います。',
  },
}

export function localizeStrategyProfile(profile: StrategyProfile): StrategyProfile {
  const override = COPY_BY_STRATEGY[profile.strategy_name]
  if (!override) return profile
  return {
    ...profile,
    ...override,
  }
}

export function resolveStrategyDisplayName(strategyName: string | null | undefined, profiles: StrategyProfile[]) {
  if (!strategyName) return null
  return profiles.find((profile) => profile.strategy_name === strategyName)?.display_name ?? strategyName
}

export function resolveRuleProfileDisplayName(ruleProfile: string | null | undefined, profiles: StrategyProfile[]) {
  if (!ruleProfile) return null
  return profiles.find((profile) => profile.rule_profile === ruleProfile)?.title ?? ruleProfile
}
