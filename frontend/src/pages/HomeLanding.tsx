import React from 'react'
import { Link } from 'react-router-dom'

const FEATURES = [
  {
    title: 'Bitcoin Treasury Insights',
    description: 'Track strategy signals and treasury metrics in one place.',
  },
  {
    title: 'Screening and Backtest',
    description: 'Run reproducible pipeline outputs from Stage2 to Backtest.',
  },
  {
    title: 'Actionable Dashboard',
    description: 'Inspect top and bottom performance with interactive charts.',
  },
]

const LOGO_PLACEHOLDERS = ['METAPLANET', 'BITCOIN.JP', 'BM JAPAN', 'PLANET GEAR']

export function HomeLanding() {
  return (
    <div className="home-landing" data-testid="home-landing-page">
      <section className="landing-hero">
        <p className="hero-kicker">METAPLANET STYLE / HOME</p>
        <h1>Build a Bitcoin-first analytics home for long-term conviction.</h1>
        <p className="hero-description">
          This page reproduces the visual structure of metaplanet.jp/en with project-safe assets and minimal-diff
          integration.
        </p>
        <div className="hero-actions">
          <button type="button" className="primary">Subscribe Updates</button>
          <Link to="/dashboard" className="secondary">Open Dashboard</Link>
        </div>
      </section>

      <section className="landing-features" aria-label="Feature cards">
        {FEATURES.map((feature) => (
          <article key={feature.title} className="feature-card">
            <h2>{feature.title}</h2>
            <p>{feature.description}</p>
          </article>
        ))}
      </section>

      <section className="landing-logos" aria-label="Partner logos">
        <h2>As seen with partners</h2>
        <div className="logo-grid">
          {LOGO_PLACEHOLDERS.map((logo) => (
            <div key={logo} className="logo-placeholder">{logo}</div>
          ))}
        </div>
      </section>

      <section className="landing-cta">
        <h2>Start from /dashboard and validate with reproducible outputs.</h2>
        <Link to="/dashboard" className="primary cta-link">Go to Dashboard</Link>
      </section>

      <style>{`
        .home-landing {
          min-height: calc(100vh - var(--nav-height));
          padding: 32px 24px 40px;
          color: #e2e8f0;
          background:
            radial-gradient(circle at 20% -10%, rgba(59, 130, 246, 0.2), transparent 35%),
            radial-gradient(circle at 80% 0%, rgba(249, 115, 22, 0.18), transparent 30%),
            #020617;
        }
        .landing-hero {
          max-width: 960px;
          margin: 0 auto 28px;
          padding: 36px;
          border: 1px solid rgba(148, 163, 184, 0.25);
          border-radius: 14px;
          background: rgba(15, 23, 42, 0.72);
          backdrop-filter: blur(2px);
        }
        .hero-kicker {
          margin: 0 0 12px;
          font-size: 12px;
          letter-spacing: 1.8px;
          color: #93c5fd;
        }
        .landing-hero h1 {
          margin: 0;
          font-size: clamp(28px, 3.8vw, 48px);
          line-height: 1.12;
          color: #f8fafc;
        }
        .hero-description {
          margin: 16px 0 0;
          max-width: 760px;
          color: #cbd5e1;
          line-height: 1.6;
        }
        .hero-actions {
          margin-top: 22px;
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
        }
        .primary,
        .secondary,
        .cta-link {
          text-decoration: none;
          border: none;
          border-radius: 999px;
          padding: 10px 18px;
          font-weight: 600;
          font-size: 13px;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
        }
        .primary,
        .cta-link {
          background: linear-gradient(90deg, #f97316, #fb7185);
          color: #fff;
        }
        .secondary {
          background: rgba(148, 163, 184, 0.15);
          color: #e2e8f0;
          border: 1px solid rgba(148, 163, 184, 0.35);
        }
        .landing-features,
        .landing-logos,
        .landing-cta {
          max-width: 960px;
          margin: 0 auto;
        }
        .landing-features {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
          gap: 12px;
          margin-bottom: 24px;
        }
        .feature-card {
          border: 1px solid rgba(148, 163, 184, 0.25);
          border-radius: 10px;
          padding: 16px;
          background: rgba(15, 23, 42, 0.66);
        }
        .feature-card h2 {
          margin: 0 0 8px;
          color: #f8fafc;
          font-size: 16px;
        }
        .feature-card p {
          margin: 0;
          color: #cbd5e1;
          font-size: 13px;
          line-height: 1.5;
        }
        .landing-logos {
          margin-bottom: 24px;
        }
        .landing-logos h2,
        .landing-cta h2 {
          margin: 0 0 12px;
          color: #f8fafc;
          font-size: 20px;
        }
        .logo-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
          gap: 10px;
        }
        .logo-placeholder {
          border: 1px dashed rgba(148, 163, 184, 0.5);
          border-radius: 8px;
          padding: 14px 12px;
          text-align: center;
          color: #cbd5e1;
          font-size: 12px;
          background: rgba(15, 23, 42, 0.66);
        }
        .landing-cta {
          border: 1px solid rgba(148, 163, 184, 0.25);
          border-radius: 12px;
          padding: 18px;
          background: rgba(15, 23, 42, 0.7);
        }
        @media (max-width: 768px) {
          .home-landing {
            padding: 24px 14px 30px;
          }
          .landing-hero {
            padding: 24px 18px;
          }
          .landing-cta h2 {
            font-size: 17px;
          }
        }
      `}</style>
    </div>
  )
}
