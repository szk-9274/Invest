/**
 * Notification Banner Component
 * Metaplanet Analytics-inspired alert/notification bar.
 * Types: info | success | warning | error
 */
import React from 'react';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface NotificationProps {
  type?: NotificationType;
  message: string;
  onDismiss?: () => void;
}

const ICONS: Record<NotificationType, string> = {
  info: 'ℹ',
  success: '✓',
  warning: '⚠',
  error: '✕',
};

export const Notification: React.FC<NotificationProps> = ({
  type = 'info',
  message,
  onDismiss,
}) => {
  return (
    <div className={`notification notification-${type}`}>
      <span className="notification-icon">{ICONS[type]}</span>
      <span className="notification-text">{message}</span>
      {onDismiss && (
        <button className="notification-close" onClick={onDismiss} aria-label="dismiss">
          ×
        </button>
      )}

      <style>{`
        .notification {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 16px;
          border-radius: var(--radius-md, 8px);
          border: 1px solid transparent;
          font-size: 14px;
          font-family: var(--font-sans, sans-serif);
          box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.08));
        }

        .notification-info {
          background: var(--info-bg, #dbeafe);
          border-color: var(--info-border, #93c5fd);
          color: #1d4ed8;
        }

        .notification-success {
          background: var(--success-bg, #dcfce7);
          border-color: var(--success-border, #86efac);
          color: #166534;
        }

        .notification-warning {
          background: var(--warning-bg, #fef9c3);
          border-color: var(--warning-border, #fde047);
          color: #854d0e;
        }

        .notification-error {
          background: var(--danger-bg, #fee2e2);
          border-color: var(--danger-border, #fca5a5);
          color: #991b1b;
        }

        .notification-icon {
          font-size: 16px;
          flex-shrink: 0;
          font-weight: 700;
        }

        .notification-text {
          flex: 1;
          line-height: 1.5;
        }

        .notification-close {
          background: none;
          border: none;
          font-size: 20px;
          cursor: pointer;
          color: inherit;
          opacity: 0.6;
          padding: 0 4px;
          line-height: 1;
          flex-shrink: 0;
          transition: opacity 0.15s;
        }

        .notification-close:hover {
          opacity: 1;
        }
      `}</style>
    </div>
  );
};
