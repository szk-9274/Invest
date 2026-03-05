/**
 * Backtest Summary Component
 * Displays key metrics from backtest results using MetricCard.
 * Metaplanet Analytics-inspired grid layout.
 */
import React from 'react';
import { BacktestSummary as BacktestSummaryData } from '../api/backtest';
import { MetricCard } from './MetricCard';

interface BacktestSummaryProps {
  data: BacktestSummaryData | null;
  loading?: boolean;
}

export const BacktestSummary: React.FC<BacktestSummaryProps> = ({ data, loading = false }) => {
  if (loading) {
    return (
      <div className="summary-state">
        <div className="summary-spinner" />
        <span>Loading metrics...</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="summary-state">
        <span className="summary-empty-text">No data available</span>
      </div>
    );
  }

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value);

  const formatPercent = (value: number) => (value * 100).toFixed(2) + '%';

  const profitFactor =
    data.avg_win !== 0 && data.avg_loss !== 0
      ? (Math.abs(data.avg_win) / Math.abs(data.avg_loss)).toFixed(2)
      : 'N/A';

  return (
    <div className="backtest-summary">
      <div className="metrics-grid">
        <MetricCard
          label="Total P&L"
          value={formatCurrency(data.total_pnl)}
          trend={data.total_pnl >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label="Total Trades"
          value={String(data.total_trades)}
          trend="neutral"
        />
        <MetricCard
          label="Win Rate"
          value={formatPercent(data.win_rate)}
          subText={`${data.winning_trades}W / ${data.losing_trades}L`}
          trend={data.win_rate >= 0.5 ? 'positive' : 'negative'}
        />
        <MetricCard
          label="Avg Win"
          value={formatCurrency(data.avg_win)}
          trend={data.avg_win >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label="Avg Loss"
          value={formatCurrency(data.avg_loss)}
          trend={data.avg_loss >= 0 ? 'positive' : 'negative'}
        />
        <MetricCard
          label="Profit Factor"
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
