import React, { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { BacktestSummary } from '../components/BacktestSummary'
import { TraderAvatar } from '../components/TraderAvatar'
import { fetchBacktestByRange, listAllBacktests, type BacktestMetadata, type BacktestResults } from '../api/backtest'
import { useBacktestDashboardContext } from './BacktestDashboard'
import { localizeStrategyProfile } from '../utils/strategyProfileLocalization'
import '../styles/dashboard-cards.css'

export const TraderStrategiesPage: React.FC = () => {
  const { t } = useTranslation()
  const { setSelectedTimestamp, strategyProfiles } = useBacktestDashboardContext()
  const traderProfiles = useMemo(
    () => strategyProfiles
      .filter((profile) => profile.is_trader_strategy)
      .map(localizeStrategyProfile)
      .sort((left, right) => (left.sort_order ?? 0) - (right.sort_order ?? 0)),
    [strategyProfiles],
  )
  const [selectedTraderId, setSelectedTraderId] = useState('')
  const [summaryResult, setSummaryResult] = useState<BacktestResults | null>(null)
  const [availableBacktests, setAvailableBacktests] = useState<BacktestMetadata[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (traderProfiles.length === 0) {
      setSelectedTraderId('')
      return
    }

    if (traderProfiles.some((profile) => profile.strategy_name === selectedTraderId)) {
      return
    }

    setSelectedTraderId(traderProfiles[0].strategy_name)
  }, [selectedTraderId, traderProfiles])

  const selectedTrader = useMemo(
    () => traderProfiles.find((profile) => profile.strategy_name === selectedTraderId) ?? traderProfiles[0] ?? null,
    [selectedTraderId, traderProfiles],
  )

  const resolvedStrategyName = useMemo(() => {
    if (!selectedTrader) return undefined
    return selectedTrader.result_strategy_name ?? selectedTrader.strategy_name ?? undefined
  }, [selectedTrader])

  useEffect(() => {
    if (!selectedTrader?.strategy_name) {
      setAvailableBacktests([])
      setSummaryResult(null)
      setLoading(false)
      return
    }

    let active = true

    const loadTraderData = async () => {
      setLoading(true)
      setError(null)

      try {
        const [backtests, latest] = await Promise.all([
          resolvedStrategyName ? listAllBacktests(resolvedStrategyName) : listAllBacktests(),
          resolvedStrategyName ? fetchBacktestByRange('ALL', resolvedStrategyName) : fetchBacktestByRange('ALL'),
        ])

        if (!active) return

        setAvailableBacktests(backtests)
        setSummaryResult(latest)
        setSelectedTimestamp(latest.timestamp)
      } catch (err) {
        if (!active) return
        setAvailableBacktests([])
        setSummaryResult(null)
        setError(err instanceof Error ? err.message : String(err))
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadTraderData()

    return () => {
      active = false
    }
  }, [resolvedStrategyName, selectedTrader, setSelectedTimestamp])

  if (!selectedTrader) {
    return <div className="dashboard-empty-panel">{t('dashboard.noBacktests')}</div>
  }

  return (
    <div className="dashboard-page-stack">
      <section className="dashboard-card">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.traderStrategiesRoute', 'Trader Strategies')}</h2>
            <p>{t('dashboard.traderStrategiesHint', 'Independent trader-inspired backtest profiles for mobile-friendly comparison.')}</p>
          </div>
        </div>

        <div className="trader-profile-grid">
          {traderProfiles.map((profile) => (
            <button
              key={profile.strategy_name}
              type="button"
              className={`trader-profile-button ${profile.strategy_name === selectedTrader.strategy_name ? 'active' : ''}`}
              onClick={() => setSelectedTraderId(profile.strategy_name)}
            >
              <span className="trader-profile-avatar">
                <TraderAvatar
                  traderKey={profile.strategy_name}
                  label={profile.display_name}
                  portraitAssetKey={profile.portrait_asset_key}
                />
              </span>
              {profile.is_current_baseline ? (
                <span className="trader-profile-badge">{t('dashboard.currentBaselineBadge', 'Current baseline')}</span>
              ) : null}
              <span className="trader-profile-name">{profile.display_name}</span>
              <span className="trader-profile-short">{profile.title}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="dashboard-card">
        <div className="dashboard-section-heading">
          <div>
            <h2>{selectedTrader.display_name}</h2>
            <p>{selectedTrader.title}</p>
          </div>
        </div>
        <p className="trader-description">{selectedTrader.description}</p>
        {error ? <p className="trader-error">{error}</p> : null}
        <BacktestSummary data={summaryResult?.summary ?? null} loading={loading} />
      </section>

      <section className="dashboard-card">
        <div className="dashboard-section-heading">
          <div>
            <h2>{t('dashboard.experimentList')}</h2>
            <p>{t('dashboard.traderStrategyRunsHint', 'Latest recorded runs for the selected trader-inspired profile.')}</p>
          </div>
        </div>
        {availableBacktests.length > 0 ? (
          <div className="backtest-list">
            {availableBacktests.map((backtest) => (
              <button
                key={backtest.timestamp}
                type="button"
                className="backtest-item"
                onClick={() => setSelectedTimestamp(backtest.timestamp)}
              >
                <div className="item-period">
                  <strong>{backtest.period}</strong>
                  <span>{t('dashboard.tradesCount', { count: backtest.trade_count })}</span>
                </div>
                <div className="item-metadata">
                  <span>{selectedTrader.display_name}</span>
                  <span>{selectedTrader.title}</span>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <p className="empty-list">{t('dashboard.noBacktests')}</p>
        )}
      </section>

      <style>{`
        .trader-profile-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 12px;
        }

        .trader-profile-button {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          min-height: 104px;
          padding: 16px 12px;
          border-radius: 16px;
          border: 1px solid #dbe4f0;
          background: #f8fafc;
          cursor: pointer;
        }

        .trader-profile-button.active {
          border-color: #3b82f6;
          background: #eff6ff;
          box-shadow: 0 10px 20px rgba(59, 130, 246, 0.12);
        }

        .trader-profile-avatar {
          display: inline-flex;
          width: 64px;
          height: 64px;
          overflow: hidden;
          border-radius: 999px;
          border: 2px solid rgba(255, 255, 255, 0.92);
          box-shadow: 0 8px 18px rgba(15, 23, 42, 0.12);
          background: #ffffff;
        }

        .trader-avatar,
        .trader-avatar__image,
        .trader-avatar svg {
          width: 100%;
          height: 100%;
          display: block;
        }

        .trader-avatar__image {
          object-fit: cover;
        }

        .trader-profile-name {
          font-weight: 700;
          color: #0f172a;
          text-align: center;
        }

        .trader-profile-badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 4px 10px;
          border-radius: 999px;
          background: #dbeafe;
          color: #1d4ed8;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.02em;
          white-space: nowrap;
        }

        .trader-profile-short {
          color: #475569;
          font-size: 13px;
          text-align: center;
        }

        .trader-description {
          margin: 0;
          color: #475569;
          line-height: 1.6;
        }

        .trader-error {
          color: #b91c1c;
          font-weight: 600;
        }
      `}</style>
    </div>
  )
}
