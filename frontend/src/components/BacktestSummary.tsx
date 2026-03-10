/**
 * Backtest Summary Component
 * Displays key metrics from backtest results using MetricCard.
 * Metaplanet Analytics-inspired grid layout.
 */
import React from 'react';
import { useTranslation } from 'react-i18next';
import { BacktestSummary as BacktestSummaryData } from '../api/backtest';
import { MetricCard } from './MetricCard';

interface BacktestSummaryProps {
  data: BacktestSummaryData | null;
  loading?: boolean;
}

export const BacktestSummary: React.FC<BacktestSummaryProps> = ({ data, loading = false }) => {
  const { t } = useTranslation();

  if (loading) {
    return (
      <div className="summary-state">
        <div className="summary-spinner" />
        <span>{t('summary.loadingMetrics')}</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="summary-state">
        <span className="summary-empty-text">{t('summary.noData')}</span>
      </div>
    );
  }

  const summary = {
    total_trades: data.total_trades ?? 0,
    winning_trades: data.winning_trades ?? 0,
    losing_trades: data.losing_trades ?? 0,
    win_rate: data.win_rate ?? 0,
    total_pnl: data.total_pnl ?? 0,
    avg_win: data.avg_win ?? 0,
    avg_loss: data.avg_loss ?? 0,
    final_capital: data.final_capital ?? 0,
    annual_return_pct: data.annual_return_pct ?? 0,
    information_ratio: data.information_ratio ?? 0,
    max_drawdown_pct: data.max_drawdown_pct ?? 0,
  }

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);

  const formatPercent = (value: number) => (value * 100).toFixed(2) + '%';

  const profitFactor =
    summary.avg_win !== 0 && summary.avg_loss !== 0
      ? (Math.abs(summary.avg_win) / Math.abs(summary.avg_loss)).toFixed(2)
      : 'N/A';

  return (
    <div className="backtest-summary">
      <div className="metrics-grid">
        <MetricCard
          label={t('summary.totalPnl')}
          value={formatCurrency(summary.total_pnl)}
          trend={summary.total_pnl >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label={t('summary.annualReturn')}
          value={formatPercent(summary.annual_return_pct)}
          trend={summary.annual_return_pct >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label={t('summary.informationRatio')}
          value={summary.information_ratio.toFixed(2)}
          trend={summary.information_ratio >= 1 ? 'positive' : summary.information_ratio < 0 ? 'negative' : 'neutral'}
        />
        <MetricCard
          label={t('summary.maxDrawdown')}
          value={formatPercent(summary.max_drawdown_pct)}
          trend={summary.max_drawdown_pct >= -0.1 ? 'neutral' : 'negative'}
        />
        <MetricCard
          label={t('summary.totalTrades')}
          value={String(summary.total_trades)}
          trend="neutral"
        />
        <MetricCard
          label={t('summary.winRate')}
          value={formatPercent(summary.win_rate)}
          subText={t('summary.winLossCompact', { wins: summary.winning_trades, losses: summary.losing_trades })}
          trend={summary.win_rate >= 0.5 ? 'positive' : 'negative'}
        />
        <MetricCard
          label={t('summary.avgWin')}
          value={formatCurrency(summary.avg_win)}
          trend={summary.avg_win >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label={t('summary.avgLoss')}
          value={formatCurrency(summary.avg_loss)}
          trend={summary.avg_loss >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label={t('summary.profitFactor')}
          value={profitFactor}
          trend={
            profitFactor === 'N/A'
              ? 'neutral'
              : parseFloat(profitFactor) >= 1.5
              ? 'positive'
              : parseFloat(profitFactor) < 1
              ? 'negative'
              : 'neutral'
          }
        />
        <MetricCard
          label={t('summary.finalCapital')}
          value={formatCurrency(summary.final_capital)}
          trend={summary.final_capital >= 0 ? 'positive' : 'negative'}
        />
      </div>

      <style>{`
        .backtest-summary {
          padding: 24px;
        }

        .summary-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 12px;
          min-height: 200px;
          color: var(--text-muted, #94a3b8);
          font-size: 14px;
        }

        .summary-spinner {
          width: 28px;
          height: 28px;
          border: 3px solid var(--border, #e2e8f0);
          border-top-color: var(--primary, #3b82f6);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .summary-empty-text {
          color: var(--text-muted, #94a3b8);
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
          gap: 16px;
        }

        @media (max-width: 768px) {
          .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
          }

          .backtest-summary {
            padding: 16px;
          }
        }
      `}</style>
    </div>
  );
};
