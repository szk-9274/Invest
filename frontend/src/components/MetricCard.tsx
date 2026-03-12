/**
 * MetricCard Component
 * Metaplanet Analytics-inspired key metric display card.
 * Shows label, large value, optional sub-text and trend indicator.
 */
import React from 'react';

export type MetricTrend = 'positive' | 'negative' | 'neutral';

export interface MetricCardProps {
  label: string;
  value: string;
  subText?: string;
  trend?: MetricTrend;
  noWrapLabel?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subText,
  trend = 'neutral',
  noWrapLabel = false,
}) => {
  return (
    <div className="metric-card">
      <div className={`metric-label ${noWrapLabel ? 'metric-label--nowrap' : ''}`}>{label}</div>
      <div className={`metric-value metric-${trend}`}>{value}</div>
      {subText && <div className="metric-sub">{subText}</div>}

      <style>{`
        .metric-card {
          background: var(--bg-card, #ffffff);
          border: 1px solid var(--border, #e2e8f0);
          border-radius: var(--radius-md, 8px);
          padding: 20px;
          min-height: 144px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          text-align: center;
          box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.08));
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .metric-card:hover {
          transform: translateY(-3px);
          box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,0.10));
        }

        .metric-label {
          font-size: 11px;
          font-weight: 600;
          color: var(--text-muted, #94a3b8);
          text-transform: uppercase;
          letter-spacing: 0.8px;
          margin-bottom: 10px;
        }

        .metric-label--nowrap {
          white-space: nowrap;
        }

        .metric-value {
          font-size: 26px;
          font-weight: 700;
          font-family: var(--font-mono, 'Monaco', monospace);
          color: var(--text-primary, #0f172a);
          line-height: 1.2;
        }

        .metric-positive {
          color: var(--success, #22c55e);
        }

        .metric-negative {
          color: var(--danger, #ef4444);
        }

        .metric-neutral {
          color: var(--text-primary, #0f172a);
        }

        .metric-sub {
          font-size: 12px;
          color: var(--text-muted, #94a3b8);
          margin-top: 6px;
          font-weight: 500;
          text-align: center;
        }
      `}</style>
    </div>
  );
};
