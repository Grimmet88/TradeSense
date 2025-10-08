// web/app.js — charts removed, confidence bars restored

const $ = (id) => document.getElementById(id);

// Controls
const riskEl = $('risk');
const regionEl = $('region');
const runBtn = $('runBtn');
const exportBtn = $('exportBtn');
const searchForm = $('searchForm');
const tickerInput = $('tickerInput');

// Lanes
const buyList = $('buyList');
const holdList = $('holdList');
const sellList = $('sellList');
const utrList = $('utrList');

// Misc
const summaryEl = $('summary');
const disclaimersEl = $('disclaimers');
const badgeEl = $('badge');

// Sidebar (compare & watchlist)
const compareForm = $('compareForm');
const compareInput = $('compareInput');
const compareRunBtn = $('compareRunBtn');
const compareList = $('compareList');
const compareResults = $('compareResults');
const watchItems = $('watchItems');

// Local state
let lastResult = null;
let watchlist = JSON.parse(localStorage.getItem('ts.watchlist') || '[]');
let compareTickers = [];

// -------------------- helpers --------------------
function esc(s = '') {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function confBarHTML(conf = 0) {
  const pct = Math.max(0, Math.min(100, Number(conf) || 0));
  return `
    <div class="conf-bar">
      <div class="conf-bar-fill" style="width:${pct}%"></div>
    </div>
  `;
}

function stockCardHTML(s) {
  const tkr = esc(s.ticker || '');
  const name = esc(s.name || '');
  const thesis = esc(s.thesis || s.whyInteresting || '');
  const tf = esc(s.timeframe || '');
  const risk = esc(s.risk || '');
  const conf = Number(s.confidence || 0);
  const cats = Array.isArray(s.catalysts) ? s.catalysts.map(esc).join('; ') : '';

  return `
    <div class="stock-card">
      <div class="stock-head">
        <div class="stock-left">
          <a href="https://finance.yahoo.com/quote/${tkr}" target="_blank" rel="noopener">${tkr}</a>
          <span>${name}</span>
        </div>
        <div class="stock-meta">${tf || '—'} • ${risk || '—'}</div>
      </div>

      <p class="thesis">${thesis}</p>
      ${cats ? `<p class="catalysts"><b>Catalysts:</b> ${cats}</p>` : ''}

      ${confBarHTML(conf)}

      <div class="actions">
        <button class="btn" data-watch="${tkr}">+ Watch</button>
        <button class="btn" data-compare="${tkr}">+ Compare</button>
      </div>
    </div>
  `;
}

function renderLane(listEl, items) {
  listEl.innerHTML = items.map(stockCardHTML).join('');
  // wire buttons
  listEl.querySelectorAll('[data-watch]').forEach(b =>
    b.addEventListener('click', () => addToWatch(b.getAttribute('data-watch')))
  );
  listEl.querySelectorAll('[data-compare]').forEach(b =>
    b.addEventListener('click', () => addCompareTicker(b.getAttribute('data-compare')))
  );
}

function renderAll(json) {
  lastResult = json;

  summaryEl.textContent = json.summary || '';
  renderLane(buyList, json.buy || []);
  renderLane(holdList, json.hold || []);
  renderLane(sellList, json.sell || []);
  renderLane(utrList, json.underTheRadar || []);

  // disclaimers
  disclaimersEl.innerHTML = (json.disclaimers || [])
    .map(d => `<div>${esc(d)}</div>`)
    .join('');

  // mock badge only if server says mock === true
  badgeEl.hidden = !(json && json.mock === true);
}

function showError(msg) {
  summaryEl.textContent = `Error: ${msg}`;
  buyList.innerHTML = holdList.innerHTML = sellList.innerHTML = utrList.innerHTML = '';
}

// -------------------- API calls --------------------
async function postJSON(url, body) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  });
  const text = await r.text();
  try {
    const json = JSON.parse(text);
    if (!r.ok && json?.error) throw new Error(json.error);
    return json;
  } catch (e) {
    throw new Error(`Bad JSON: ${text.slice(0, 160)}`);
  }
}

// -------------------- actions --------------------
async function runAnalysis() {
  try {
    runBtn.disabled = true;
    const risk = riskEl.value || 'medium';
    const region = regionEl.value || 'US';
    const json = await postJSON('/api/screen', { risk, region });
    renderAll(json);
  } catch (e) {
    console.error(e);
    showError(e.message || 'Failed');
  } finally {
    runBtn.disabled = false;
  }
}

async function analyzeTicker(ticker) {
  if (!ticker) return;
  try {
    const json = await postJSON('/api/analyze', { ticker });
    renderAll(json);
  } catch (e) {
    console.error(e);
    showError(e.message || 'Failed');
  }
}

// Export CSV
function exportCSV() {
  if (!lastResult) return;
  const rows = [];
  const pushRows = (arr, lane) => (arr || []).forEach(x => rows.push([
    lane, x.ticker, x.name || '', x.timeframe || '', x.risk || '',
    x.confidence ?? '', (x.thesis || x.whyInteresting || '').replace(/\s+/g,' '),
    Array.isArray(x.catalysts) ? x.catalysts.join('; ') : ''
  ]));
  pushRows(lastResult.buy, 'BUY');
  pushRows(lastResult.hold, 'HOLD');
  pushRows(lastResult.sell, 'SELL');
  pushRows(lastResult.underTheRadar, 'UTR');

  const csv = [
    ['Lane','Ticker','Name','Timeframe','Risk','Confidence','Thesis','Catalysts'].join(','),
    ...rows.map(r => r.map(v => `"${String(v).replaceAll('"','""')}"`).join(','))
  ].join('\n');

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'TradeSense_analysis.csv'; a.click();
  URL.revokeObjectURL(url);
}

// -------------------- compare + watchlist (no charts) --------------------
function saveWatch() { localStorage.setItem('ts.watchlist', JSON.stringify(watchlist)); renderWatch(); }
function addToWatch(t) { t = (t || '').toUpperCase(); if (!t) return; if (!watchlist.includes(t)) watchlist.push(t); saveWatch(); }
function removeFromWatch(t) { watchlist = watchlist.filter(x => x !== t); saveWatch(); }
function renderWatch() {
  if (!watchItems) return;
  if (!watchlist.length) { watchItems.innerHTML = '<div class="muted">No symbols yet.</div>'; return; }
  watchItems.innerHTML = watchlist.map(t => `
    <div class="row" style="justify-content:space-between">
      <span>${t}</span>
      <div style="display:flex;gap:8px">
        <button class="btn" data-an="${t}">Analyze</button>
        <button class="btn" data-rm="${t}">Remove</button>
      </div>
    </div>
  `).join('');
  watchItems.querySelectorAll('[data-an]').forEach(b => b.addEventListener('click', () => analyzeTicker(b.getAttribute('data-an'))));
  watchItems.querySelectorAll('[data-rm]').forEach(b => b.addEventListener('click', () => removeFromWatch(b.getAttribute('data-rm'))));
}
function addCompareTicker(t){ t=(t||'').toUpperCase(); if(!t) return; if(!compareTickers.includes(t)) compareTickers.push(t); renderCompareList(); }
function removeCompareTicker(t){ compareTickers = compareTickers.filter(x=>x!==t); renderCompareList(); }
function renderCompareList(){
  if(!compareList) return;
  if(!compareTickers.length){ compareList.innerHTML = '<div class="muted">Add tickers to compare.</div>'; return; }
  compareList.innerHTML = compareTickers.map(t => `
    <div class="row" style="justify-content:space-between">
      <span>${t}</span>
      <button class="btn" data-del="${t}">Remove</button>
    </div>
  `).join('');
  compareList.querySelectorAll('[data-del]').forEach(b => b.addEventListener('click', () => removeCompareTicker(b.getAttribute('data-del'))));
}
function runCompare(){ /* charts removed — keep list only */ }

// -------------------- wire up --------------------
runBtn?.addEventListener('click', runAnalysis);
exportBtn?.addEventListener('click', exportCSV);
searchForm?.addEventListener('submit', (e) => {
  e.preventDefault();
  analyzeTicker((tickerInput?.value || '').trim());
});
compareForm?.addEventListener('submit', (e) => {
  e.preventDefault();
  const v = (compareInput?.value || '').trim();
  if (v) { addCompareTicker(v); compareInput.value=''; }
});
compareRunBtn?.addEventListener('click', runCompare);

// initial renders
renderWatch();
renderCompareList();

// Optionally auto-run once:
// runAnalysis();
