/**
 * Chart Gallery Component
 * Displays backtest chart images in a grid
 */
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ChartGalleryProps {
  charts: Record<string, string | null>;
  loading?: boolean;
}

export const ChartGallery: React.FC<ChartGalleryProps> = ({ charts, loading = false }) => {
  const { t } = useTranslation();
  const [selectedChart, setSelectedChart] = useState<string | null>(null);

  if (loading) {
    return <div className="chart-gallery loading">{t('chartGallery.loadingCharts')}</div>;
  }

  const chartEntries = Object.entries(charts).filter(([_, image]) => image !== null);

  if (chartEntries.length === 0) {
    return <div className="chart-gallery empty">{t('chartGallery.noCharts')}</div>;
  }

  const topCharts = chartEntries.filter(([key]) => key.startsWith('top_'));
  const bottomCharts = chartEntries.filter(([key]) => key.startsWith('bottom_'));
  const otherCharts = chartEntries.filter(
    ([key]) => !key.startsWith('top_') && !key.startsWith('bottom_')
  );

  return (
    <div className="chart-gallery">
      {topCharts.length > 0 && (
        <div className="chart-section">
          <h3>{t('chartGallery.topWinners')}</h3>
          <div className="chart-grid">
            {topCharts.map(([key, image]) => (
              <div
                key={key}
                className="chart-item"
                onClick={() => setSelectedChart(key)}
                style={{ cursor: 'pointer' }}
              >
                <img src={image!} alt={key} />
                <div className="chart-label">{key.replace(/_/g, ' ')}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {bottomCharts.length > 0 && (
        <div className="chart-section">
          <h3>{t('chartGallery.bottomLosers')}</h3>
          <div className="chart-grid">
            {bottomCharts.map(([key, image]) => (
              <div
                key={key}
                className="chart-item"
                onClick={() => setSelectedChart(key)}
                style={{ cursor: 'pointer' }}
              >
                <img src={image!} alt={key} />
                <div className="chart-label">{key.replace(/_/g, ' ')}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {otherCharts.length > 0 && (
        <div className="chart-section">
          <h3>{t('chartGallery.otherCharts')}</h3>
          <div className="chart-grid">
            {otherCharts.map(([key, image]) => (
              <div
                key={key}
                className="chart-item"
                onClick={() => setSelectedChart(key)}
                style={{ cursor: 'pointer' }}
              >
                <img src={image!} alt={key} />
                <div className="chart-label">{key.replace(/_/g, ' ')}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal for enlarged view */}
      {selectedChart && charts[selectedChart] && (
        <div className="chart-modal" onClick={() => setSelectedChart(null)}>
          <div className="modal-content">
            <button className="close-button" onClick={() => setSelectedChart(null)}>
              ×
            </button>
            <img src={charts[selectedChart]!} alt={selectedChart} />
            <div className="modal-title">{selectedChart.replace(/_/g, ' ')}</div>
          </div>
        </div>
      )}

      <style>{`
        .chart-gallery {
          padding: 20px;
        }

        .chart-gallery.loading,
        .chart-gallery.empty {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 300px;
          color: #666;
        }

        .chart-section {
          margin-bottom: 30px;
        }

        .chart-section h3 {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 15px;
          color: #333;
          border-bottom: 2px solid #ddd;
          padding-bottom: 10px;
        }

        .chart-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 15px;
        }

        .chart-item {
          background: #f5f5f5;
          border: 1px solid #ddd;
          border-radius: 8px;
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .chart-item:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .chart-item img {
          width: 100%;
          height: auto;
          display: block;
        }

        .chart-label {
          padding: 10px;
          font-size: 12px;
          color: #666;
          text-align: center;
          background: #fff;
          border-top: 1px solid #ddd;
        }

        .chart-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          position: relative;
          max-width: 90vw;
          max-height: 90vh;
          background: white;
          border-radius: 8px;
          overflow: auto;
        }

        .close-button {
          position: absolute;
          top: 10px;
          right: 10px;
          width: 40px;
          height: 40px;
          border: none;
          background: rgba(0, 0, 0, 0.5);
          color: white;
          font-size: 24px;
          cursor: pointer;
          border-radius: 4px;
          z-index: 1001;
        }

        .close-button:hover {
          background: rgba(0, 0, 0, 0.7);
        }

        .modal-content img {
          width: 100%;
          height: auto;
          display: block;
        }

        .modal-title {
          padding: 15px;
          text-align: center;
          background: #f5f5f5;
          border-top: 1px solid #ddd;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};
