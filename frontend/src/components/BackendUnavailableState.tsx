import React from 'react'
import { useTranslation } from 'react-i18next'

interface BackendUnavailableStateProps {
  detail: string
  onRetry: () => Promise<void>
}

const LOCAL_BACKEND_COMMAND = './python/.venv/bin/python3 -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000'

export const BackendUnavailableState: React.FC<BackendUnavailableStateProps> = ({ detail, onRetry }) => {
  const { t } = useTranslation()

  return (
    <section className="backend-unavailable-state" data-testid="backend-unavailable-state">
      <div className="backend-unavailable-state__badge">{t('dashboard.backendUnavailableBadge', 'localhost')}</div>
      <h2>{t('dashboard.backendUnavailableTitle', 'Backend unavailable on localhost')}</h2>
      <p>{t('dashboard.backendUnavailableDescription', 'The dashboard could not reach the backend API. Start the backend service and retry.')}</p>
      <p>{t('dashboard.backendUnavailableHint', 'Recommended local command:')}</p>
      <code>{LOCAL_BACKEND_COMMAND}</code>
      <p className="backend-unavailable-state__detail">{detail}</p>
      <button type="button" onClick={() => void onRetry()}>
        {t('dashboard.backendUnavailableRetry', 'Retry connection')}
      </button>

      <style>{`
        .backend-unavailable-state {
          display: grid;
          gap: 12px;
          padding: 20px;
          border-radius: 16px;
          border: 1px solid #fcd34d;
          background: #fffbeb;
          color: #78350f;
          box-shadow: 0 10px 24px rgba(120, 53, 15, 0.08);
        }

        .backend-unavailable-state__badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: fit-content;
          padding: 4px 10px;
          border-radius: 999px;
          background: #fef3c7;
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }

        .backend-unavailable-state h2 {
          margin: 0;
          font-size: 22px;
        }

        .backend-unavailable-state p {
          margin: 0;
          line-height: 1.6;
        }

        .backend-unavailable-state code {
          display: block;
          overflow-x: auto;
          padding: 12px 14px;
          border-radius: 12px;
          background: rgba(120, 53, 15, 0.08);
          font-size: 13px;
        }

        .backend-unavailable-state__detail {
          color: #92400e;
          font-size: 13px;
        }

        .backend-unavailable-state button {
          width: fit-content;
          padding: 10px 14px;
          border: none;
          border-radius: 999px;
          background: #b45309;
          color: #ffffff;
          font-weight: 700;
          cursor: pointer;
        }
      `}</style>
    </section>
  )
}
