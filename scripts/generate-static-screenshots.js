const fs = require('fs');

const sampleAssets = [
  { ticker: 'AAA', purchases: [ {t: 1672531200000, price: 100, amount: 200}, {t:1672617600000, price:110, amount:240}, {t:1672704000000, price:105, amount:180} ] , totalPnl:300, group:'top' },
  { ticker: 'BBB', purchases: [ {t:1672531200000, price: 80, amount: 150}, {t:1672617600000, price:82, amount:160} ], totalPnl:100, group:'top' },
  { ticker: 'CCC', purchases: [ {t:1672531200000, price: 50, amount: 200}, {t:1672617600000, price:45, amount:220}, {t:1672704000000, price:48, amount:120} ], totalPnl:-200, group:'bottom' },
];

function calculateSize(amount, scale=0.12){
  if(!isFinite(amount) || amount<=0) return 6;
  return Math.max(6, Math.min(28, Math.round(Math.sqrt(amount)*scale*100)/100));
}

function renderGrid(width, height, outPath){
  const cols = 5;
  const rows = 2;
  const padding = 20;
  const chartW = Math.floor((width - padding*(cols+1)) / cols);
  const chartH = Math.floor((height - padding*(rows+1)) / rows);

  const now = Date.now();
  let svg = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns='http://www.w3.org/2000/svg' width='${width}' height='${height}' viewBox='0 0 ${width} ${height}'>\n`;
  svg += `<rect width='100%' height='100%' fill='#f8fafc' />\n`;

  const items = [];
  // expand items to 10 deterministic cards by cycling sampleAssets
  for(let i=0;i<10;i++) items.push(sampleAssets[i % sampleAssets.length]);

  items.forEach((item, idx) => {
    const col = idx % cols;
    const row = Math.floor(idx / cols);
    const x = padding + col*(chartW + padding);
    const y = padding + row*(chartH + padding);
    svg += `<g transform='translate(${x},${y})'>\n`;
    svg += `<rect x='0' y='0' width='${chartW}' height='${chartH}' rx='8' fill='#fff' stroke='#e2e8f0' />\n`;
    svg += `<text x='12' y='20' font-family='sans-serif' font-size='12' fill='#0f172a'>${item.ticker} <tspan font-size='10' fill='#475569'>${item.group.toUpperCase()}</tspan></text>\n`;

    const marginLeft = 40;
    const marginTop = 30;
    const plotW = chartW - marginLeft - 12;
    const plotH = chartH - marginTop - 20;

    const prices = item.purchases.map(p=>p.price);
    const times = item.purchases.map(p=>p.t);
    const minP = Math.min(...prices);
    const maxP = Math.max(...prices);
    const minT = Math.min(...times);
    const maxT = Math.max(...times);

    item.purchases.forEach((pt, i) => {
      const tx = marginLeft + ((pt.t - minT) / (maxT - minT || 1)) * plotW;
      const ty = marginTop + (1 - (pt.price - minP) / (maxP - minP || 1)) * plotH;
      const r = calculateSize(pt.amount);
      const color = item.totalPnl>=0 ? '#22c55e' : '#ef4444';
      svg += `<circle cx='${tx}' cy='${ty}' r='${r}' fill='${color}' fill-opacity='0.8' stroke='#08306b' stroke-width='0.5' />\n`;
    });

    svg += `</g>\n`;
  });

  svg += `</svg>`;
  fs.mkdirSync(require('path').dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, svg, 'utf8');
  console.log('Wrote', outPath);
}

renderGrid(1280, 720, 'tests/screenshots/desktop.svg');
renderGrid(375, 812, 'tests/screenshots/mobile.svg');
