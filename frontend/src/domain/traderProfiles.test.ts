import { describe, expect, it } from 'vitest'
import { getTraderProfileOverride, getTraderVisual, isKnownTraderStrategy } from './traderProfiles'

describe('traderProfiles manifest', () => {
  it('provides localized copy and visual metadata from one source', () => {
    const profile = getTraderProfileOverride('minervini-trend')
    const visual = getTraderVisual('minervini-trend', 'minervini')

    expect(profile?.display_name).toBe('マーク・ミネルヴィニ')
    expect(profile?.title).toBe('トレンドテンプレート主導')
    expect(visual?.portraitSrc).toContain('minervini.png')
    expect(visual?.fallbackPalette.accent).toBe('#c026d3')
  })

  it('distinguishes known trader strategies from baseline strategies', () => {
    expect(isKnownTraderStrategy('buffett-quality')).toBe(true)
    expect(isKnownTraderStrategy('rule-based-stage2')).toBe(false)
  })
})
