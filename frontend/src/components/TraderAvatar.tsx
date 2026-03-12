import React from 'react'
import { getTraderVisual, type TraderPalette } from '../domain/traderProfiles'

type TraderAvatarProps = {
  traderKey: string
  label: string
  portraitAssetKey?: string | null
}

function TraderAvatarFallback({ label, palette }: { label: string; palette: TraderPalette }) {
  return (
    <svg viewBox="0 0 80 80" role="img" aria-label={`${label} portrait`}>
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
  )
}

export const TraderAvatar: React.FC<TraderAvatarProps> = ({ traderKey, label, portraitAssetKey }) => {
  const visual = getTraderVisual(traderKey, portraitAssetKey)
  const [imageFailed, setImageFailed] = React.useState(false)

  React.useEffect(() => {
    setImageFailed(false)
  }, [traderKey])

  return (
    <span className="trader-avatar">
      {visual.portraitSrc && !imageFailed ? (
        <img
          src={visual.portraitSrc}
          alt={`${label} portrait`}
          className="trader-avatar__image"
          loading="lazy"
          decoding="async"
          onError={() => setImageFailed(true)}
        />
      ) : (
        <TraderAvatarFallback label={label} palette={visual.fallbackPalette} />
      )}
    </span>
  )
}
