const http = require('http');
const { URL } = require('url');

const sampleTrades = [
  { ticker: 'AAA', entry_date: '2026-01-01T00:00:00Z', entry_price: 100, exit_date: '2026-01-10T00:00:00Z', exit_price: 110, exit_reason: 'rule', shares: 2, pnl: 20, pnl_pct: 0.1 },
  { ticker: 'CCC', entry_date: '2026-01-03T00:00:00Z', entry_price: 50, exit_date: '2026-01-09T00:00:00Z', exit_price: 45, exit_reason: 'rule', shares: 4, pnl: -20, pnl_pct: -0.1 },
];

const sampleStats = [
  { ticker: 'AAA', total_pnl: 300, trade_count: 3 },
  { ticker: 'BBB', total_pnl: 100, trade_count: 2 },
  { ticker: 'CCC', total_pnl: -200, trade_count: 4 },
];

function makeResults(timestamp = '2026-03-07_000000') {
  return {
    timestamp,
    summary: { total_trades: 2, winning_trades: 1, losing_trades: 1, win_rate: 0.5, total_pnl: 280, avg_win: 20, avg_loss: -20 },
    trades: sampleTrades,
    ticker_stats: sampleStats,
    charts: {},
  };
}

function sendJson(res, status, obj) {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
  res.writeHead(status, headers);
  res.end(JSON.stringify(obj));
}

const server = http.createServer((req, res) => {
  try {
    if (req.method === 'OPTIONS') {
      res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      });
      return res.end();
    }

    const parsed = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const path = parsed.pathname;

    if (req.method === 'GET' && path === '/health') {
      return sendJson(res, 200, { status: 'ok' });
    }

    if (req.method === 'GET' && path === '/api/backtest/list') {
      return sendJson(res, 200, {
        backtests: [
          {
            timestamp: '2026-03-07_000000',
            start_date: '2026-01-01',
            end_date: '2026-02-01',
            period: '2026-01',
            trade_count: 2,
            dir_name: '',
          },
        ],
      });
    }

    if (req.method === 'GET' && path === '/api/backtest/latest') {
      return sendJson(res, 200, makeResults());
    }

    if (req.method === 'GET' && path.startsWith('/api/backtest/results/')) {
      const parts = path.split('/');
      const ts = parts[parts.length - 1] || '';
      if (!ts) return sendJson(res, 400, { error: 'missing timestamp' });
      return sendJson(res, 200, makeResults(ts));
    }

    // Not found
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'not found' }));
  } catch (err) {
    console.error('mock-backend error', err);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'internal error' }));
  }
});

const port = process.env.PORT || 8000;
server.listen(port, () => console.log(`Mock backend listening on ${port}`));

// Graceful shutdown support for CI
function shutdown(signal) {
  console.log(`${signal} received, shutting down mock backend`);
  server.close(() => process.exit(0));
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
