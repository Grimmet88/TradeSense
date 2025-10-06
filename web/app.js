// web/app.js
/* TradeSense – Analysis UI logic (Buy/Hold/Sell, single-ticker analyze, compare, watchlist) */

const $ = (id) => document.getElementById(id);

// Controls / panes
const riskSel = $('risk');
const regionSel = $('region');
const runBtn = $('runBtn');
const exportBtn = $('exportBtn');

const summaryEl = $('summary');
const buyList = $('buyList');
const holdList = $('holdList');
const sellList = $('sellList');
const utrList = $('utrList');
const disclaimersEl = $('disclaimers');
const badgeEl = $('badge');

// Search single ticker
const searchForm = $('searchForm');
const tickerInput = $('tickerInput');

// Right sidebar: compare + watchlist
const compareForm = $('compareForm');
const compareInput = $('compareInput');
const compareRunBtn = $('compareRunBtn');
const compareList = $('compareList');
const compareResults = $('compareResults');

const watchItems = $('watchItems');

let lastResult = null; // keep most-recent screen/analyze payload for export, etc.

// -------- Utilities --------
function fmtPct(n) { return `${Math.max(0, Math.min(100, Math.round(n)))}%`; }
function esc(s='') { return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// cache tiny GETs (per page life)
const mem = new Map();
async function getJSON(url) {
  if (mem.has(url)) return mem.get(url);
  const p = fetch(url, { headers: { 'Accept': 'application/json' } }).then(async r => {
    const j = await r.json();
    if (!r.ok) throw new Error(j?.error || `HTTP ${r.status}`);
    return j;
  });
  mem.set(url, p);
  return p;
}

async function postJSON(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json', 'Accept':'application/json'},
    body: JSON.stringify(body||{})
  });
  const j = await r.json().catch(()=> ({}));
  if (!r.ok) throw new Error(j?.error || `HTTP ${r.status}`);
  return j;
}

// -------- Charts (sparklines) --------
async function renderSparkline(canvas, ticker, days=180) {
  try {
    const data = await getJSON(`/api/series?ticker=${encodeURIComponent(ticker)}&days=${days}`);
    const xs = data.series.map(p => new Date(p.t));
    const ys = data.series.map(p => p.close);

    if (!xs.length) {
      canvas.replaceWith(elNode(`<div class="text-sm" style="color:#9ab3cc">No price data</div>`));
      return;
    }

    // Chart.js (already loaded in analysis.html)
    const ctx = canvas.getContext('2d');
    // destroy old chart if any
    if (canvas._ch) { canvas._ch.destroy(); }

    canvas._ch = new Chart(ctx, {
      type: 'line',
      data: { labels: xs, datasets: [{ data: ys, fill: false, tension: 0.25 }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        elements: { point: { radius: 0 } },
        scales: { x: { display: false }, y: { display: false } }
      }
    });
  } catch (e) {
    canvas.replaceWith(elNode(`<div class="text-sm" style="color:#9ab3cc">Chart error</div>`));
    console.error('[sparkline]', ticker, e);
  }
}

// -------- Rendering --------
function elNode(html) {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

function stockCard(item, lane='buy') {
  const {
    ticker='', name='', thesis='',
    timeframe='', confidence=0, risk='',
    catalysts = []
  } = item;

  const confW = Math.max(0, Math.min(100, Number(confidence)||0));

  const catalystsHtml = Array.isArray(catalysts) && catalysts.length
    ? `<div class="text-sm" style="color:#9ab3cc"><strong>Catalysts:</strong> ${catalysts.map(esc).join('; ')}</div>`
    : '';

  const card = elNode(`
    <article class="stock-card card">
      <div style="display:flex; justify-content:space-between; align-items:baseline; gap:8px;">
        <h3>${esc(ticker)} <span style="color:#9ab3cc; font-weight:400;">${esc(name)}</span></h3>
        <span class="badge" style="color:#9ab3cc">${esc(timeframe)} • ${esc(risk)}</span>
      </div>

      <p>${esc(thesis)}</p>

      <div class="conf-bar" title="Confidence: ${fmtPct(confW)}">
        <div class="conf-bar-fill" style="width:${confW}%;"></div>
      </div>

      ${catalystsHtml}

      <div style="height:80px; margin-top:8px;">
        <canvas width="300" height="80"></canvas>
      </div>

      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
        <button class="btn" data-watch="${esc(ticker)}">+ Watch</button>
        <button class="btn" data-compare="${esc(ticker)}">+ Compare</button>
      </div>
    </article>
  `);

  // hook watch / compare buttons
  card.querySelectorAll('[data-watch]').forEach(b=>{
    b.addEventListener('click', ()=> addToWatchlist(ticker));
  });
  card.querySelectorAll('[data-compare]').forEach(b=>{
    b.addEventListener('click', ()=> addToCompare(ticker));
  });

  // draw sparkline
  const canvas = card.querySelector('canvas');
  renderSparkline(canvas, ticker).catch(()=>{});

  return card;
}

function renderResult(json, from='screen') {
  lastResult = json;

  // Summary
  summaryEl.innerHTML = esc(json.summary || '');

// lanes
  const lanes = [
    [buyList, json.buy],
    [holdList, json.hold],
    [sellList, json.sell]
  ];
  lanes.forEach(([root, arr]) => {
    root.innerHTML = '';
    if (Array.isArray(arr)) {
      arr.forEach(it => root.appendChild(stockCard(it)));
    }
  });

  // Under the radar
  utrList.innerHTML = '';
  if (Array.isArray(json.underTheRadar)) {
    json.underTheRadar.forEach(it => {
      const card = elNode(`
        <article class="stock-card card">
          <div style="display:flex; justify-content:space-between; align-items:baseline; gap:8px;">
            <h3>${esc(it.ticker || '')} <span style="color:#9ab3cc; font-weight:400;">${esc(it.name || '')}</span></h3>
            <span class="badge" style="color:#9ab3cc">${esc(it.timeframe || '')} • ${esc(it.risk || '')}</span>
          </div>
          <p>${esc(it.whyInteresting || it.thesis || '')}</p>
          <div class="conf-bar"><div class="conf-bar-fill" style="width:${fmtPct(it.confidence||0)}"></div></div>
          <div style="height:80px; margin-top:8px;">
            <canvas width="300" height="80"></canvas>
          </div>
          <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
            <button class="btn" data-watch="${esc(it.ticker || '')}">+ Watch</button>
            <button class="btn" data-compare="${esc(it.ticker || '')}">+ Compare</button>
          </div>
        </article>
      `);
      card.querySelectorAll('[data-watch]').forEach(b=>{
        b.addEventListener('click', ()=> addToWatchlist(it.ticker));
      });
      card.querySelectorAll('[data-compare]').forEach(b=>{
        b.addEventListener('click', ()=> addToCompare(it.ticker));
      });
      const canvas = card.querySelector('canvas');
      if (it.ticker) renderSparkline(canvas, it.ticker).catch(()=>{});
      utrList.appendChild(card);
    });
  }

  // Disclaimers
  const d = Array.isArray(json.disclaimers) ? json.disclaimers : [];
  disclaimersEl.innerHTML = d.map(t => `<div style="color:#9ab3cc">${esc(t)}</div>`).join('');

  // Hide/show mock badge based on whether response looks mocked
  const mockish =
    (json.buy?.some(x => x.ticker === 'XOM') && json.hold?.some(x => x.ticker === 'NVDA')) ||
    /not financial advice/i.test((json.disclaimers||[]).join(' '));
  badgeEl.hidden = !mockish;
}

// -------- Actions --------
async function runScreen() {
  try {
    summaryEl.innerHTML = '<em>Analyzing…</em>';
    [buyList, holdList, sellList, utrList].forEach(el => el.innerHTML = '');
    const body = { risk: riskSel.value, region: regionSel.value };
    const json = await postJSON('/api/screen', body);
    renderResult(json, 'screen');
  } catch (e) {
    console.error('[screen]', e);
    summaryEl.innerHTML = `<span style="color:#e88">Error: ${esc(e.message)}</span>`;
  }
}

async function analyzeTicker(ticker) {
  const t = (ticker || '').trim().toUpperCase();
  if (!t) return;
  try {
    summaryEl.innerHTML = `<em>Analyzing ${esc(t)}…</em>`;
    [buyList, holdList, sellList, utrList].forEach(el => el.innerHTML = '');
    const json = await postJSON('/api/analyze', { ticker: t });
    renderResult(json, 'analyze');
  } catch (e) {
    console.error('[analyze]', e);
    summaryEl.innerHTML = `<span style="color:#e88">Error: ${esc(e.message)}</span>`;
  }
}

// -------- Export CSV --------
function toCSV(rows) {
  const escCSV = (v='') => `"${String(v).replace(/"/g,'""')}"`;
  const header = ['lane','ticker','name','confidence','risk','timeframe','thesis','catalysts'].map(escCSV).join(',');
  const lines = [header];

  const pushLane = (lane, arr=[]) => arr.forEach(it=>{
    lines.push([
      lane, it.ticker, it.name, it.confidence, it.risk, it.timeframe,
      it.thesis || it.whyInteresting || '',
      Array.isArray(it.catalysts) ? it.catalysts.join('; ') : ''
    ].map(escCSV).join(','));
  });

  pushLane('BUY', lastResult?.buy);
  pushLane('HOLD', lastResult?.hold);
  pushLane('SELL', lastResult?.sell);
  pushLane('UTR', lastResult?.underTheRadar);

  return lines.join('\n');
}

function download(name, content, mime='text/plain') {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = name;
  document.body.appendChild(a); a.click();
  setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 0);
}

// -------- Compare (sidebar) --------
const compareSet = new Set();

function renderCompareList() {
  compareList.innerHTML = '';
  if (!compareSet.size) {
    compareList.innerHTML = `<div class="text-sm" style="color:#9ab3cc">Add tickers to compare.</div>`;
    return;
  }
  compareSet.forEach(t=>{
    const row = elNode(`
      <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; border:1px solid #1e2a3b; border-radius:8px; padding:6px 8px; margin-bottom:6px;">
        <strong>${esc(t)}</strong>
        <button class="btn" data-remove="${esc(t)}">Remove</button>
      </div>
    `);
    row.querySelector('[data-remove]').addEventListener('click', ()=> {
      compareSet.delete(t);
      renderCompareList();
    });
    compareList.appendChild(row);
  });
}

function addToCompare(ticker) {
  if (!ticker) return;
  compareSet.add(ticker.toUpperCase());
  renderCompareList();
}

async function runCompare() {
  compareResults.innerHTML = '';
  if (!compareSet.size) {
    compareResults.innerHTML = `<div class="card">No tickers to compare yet.</div>`;
    return;
  }
  for (const t of compareSet) {
    const card = elNode(`
      <div class="card" style="display:grid; gap:6px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong>${esc(t)}</strong>
          <span class="text-sm" style="color:#9ab3cc">180d</span>
        </div>
        <div style="height:100px;"><canvas width="320" height="100"></canvas></div>
      </div>
    `);
    compareResults.appendChild(card);
    const canvas = card.querySelector('canvas');
    renderSparkline(canvas, t, 180).catch(()=>{});
    // small breath to avoid hammering provider
    await sleep(120);
  }
}

// -------- Watchlist (localStorage) --------
const WATCH_KEY = 'tradesense.watch';
function loadWatch() {
  try {
    const arr = JSON.parse(localStorage.getItem(WATCH_KEY) || '[]');
    return Array.isArray(arr) ? arr : [];
  } catch { return []; }
}
function saveWatch(arr) { localStorage.setItem(WATCH_KEY, JSON.stringify(arr)); }

function renderWatch() {
  const arr = loadWatch();
  watchItems.innerHTML = '';
  if (!arr.length) {
    watchItems.innerHTML = `<div class="text-sm" style="color:#9ab3cc">No symbols yet.</div>`;
    return;
  }
  arr.forEach(t=>{
    const row = elNode(`
      <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; border:1px solid #1e2a3b; border-radius:8px; padding:6px 8px; margin-bottom:6px;">
        <span>${esc(t)}</span>
        <div style="display:flex; gap:6px;">
          <button class="btn" data-analyze="${esc(t)}">Analyze</button>
          <button class="btn" data-del="${esc(t)}">Remove</button>
        </div>
      </div>
    `);
    row.querySelector('[data-analyze]').addEventListener('click', ()=> analyzeTicker(t));
    row.querySelector('[data-del]').addEventListener('click', ()=>{
      const next = loadWatch().filter(x => x !== t);
      saveWatch(next); renderWatch();
    });
    watchItems.appendChild(row);
  });
}

function addToWatchlist(t) {
  const u = (t||'').toUpperCase();
  if (!u) return;
  const arr = loadWatch();
  if (!arr.includes(u)) {
    arr.push(u); saveWatch(arr); renderWatch();
  }
}

// -------- Wire up events --------
runBtn?.addEventListener('click', runScreen);

exportBtn?.addEventListener('click', ()=>{
  if (!lastResult) return alert('Run an analysis first.');
  const csv = toCSV([]);
  download(`tradesense_${Date.now()}.csv`, toCSV(), 'text/csv');
});

// Single ticker search
searchForm?.addEventListener('submit', (e)=>{
  e.preventDefault();
  const t = tickerInput?.value || '';
  analyzeTicker(t);
});

// Compare form
compareForm?.addEventListener('submit', (e)=>{
  e.preventDefault();
  const t = (compareInput?.value || '').trim().toUpperCase();
  if (t) addToCompare(t);
  compareInput.value = '';
});
compareRunBtn?.addEventListener('click', runCompare);

// Initial UI state
renderCompareList();
renderWatch();
summaryEl.innerHTML = `<em>Click “Run Analysis” or analyze a specific ticker.</em>`;
