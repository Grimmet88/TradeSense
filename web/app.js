// ---------- Helpers ----------
const $ = (id) => document.getElementById(id);
const state = {
  mock: false,
  screen: null,            // latest screen JSON
  watchlist: loadWatchlist(),
  compareSet: new Set(),   // tickers selected for compare
  charts: new Map(),       // ticker -> Chart instance
};

function loadWatchlist(){
  try { return JSON.parse(localStorage.getItem('ts_watchlist')||'[]'); }
  catch { return []; }
}
function saveWatchlist(){ localStorage.setItem('ts_watchlist', JSON.stringify(state.watchlist)); }

async function post(path, body) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 10000);
  try {
    const res = await fetch(path, {
      method: 'POST', headers: { 'Content-Type':'application/json' },
      body: JSON.stringify(body || {}), signal: ctrl.signal
    });
    clearTimeout(t);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    state.mock = true;
    $('badge').hidden = false;
    // Minimal mock to keep UI alive
    return {
      summary:"Offline demo mode. Showing mock data.",
      buy:[ {ticker:"XOM",name:"Exxon Mobil",thesis:"Cash flow + dividend",timeframe:"medium",confidence:82,risk:"medium",catalysts:["OPEC","Margins"]} ],
      hold:[ {ticker:"NVDA",name:"NVIDIA",thesis:"Leader, rich valuation",timeframe:"short",confidence:74,risk:"medium",catalysts:["DC demand"]} ],
      sell:[ {ticker:"RIVN",name:"Rivian",thesis:"Cash burn risks",timeframe:"short",confidence:70,risk:"high",catalysts:["Deliveries"]} ],
      underTheRadar:[ {ticker:"INMD",name:"InMode",whyInteresting:"High-margin medtech",timeframe:"medium",confidence:65,risk:"medium",catalysts:["Approvals"]} ],
      disclaimers:["This is not financial advice.","Do your own research."]
    };
  }
}

async function get(path) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 10000);
  try {
    const res = await fetch(path, { signal: ctrl.signal });
    clearTimeout(t);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    // fallback synthetic series
    const now = Date.now(), oneDay=86400000;
    const series = Array.from({length:120}, (_,i)=>({t: now-(119-i)*oneDay, close: 100+i*0.1 + Math.sin(i/9)*2}));
    return { ticker: 'DEMO', series };
  }
}

function pct(n){ return Math.max(0, Math.min(100, Number(n)||0)); }

function csvEscape(s){ return `"${String(s).replaceAll('"','""')}"`; }
function downloadCSV(filename, rows) {
  const csv = rows.map(r => r.map(csvEscape).join(',')).join('\n');
  const blob = new Blob([csv], {type:'text/csv;charset=utf-8;'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

// ---------- UI Rendering ----------
function ideaActions(ticker, name){
  const inWatch = state.watchlist.includes(ticker);
  return `
    <div class="actions">
      <button class="smallbtn add-watch" data-t="${ticker}" data-n="${name}">${inWatch?'✓ In Watchlist':'+ Watch'}</button>
      <button class="smallbtn view-chart" data-t="${ticker}">Chart</button>
      <button class="smallbtn add-compare" data-t="${ticker}">Compare</button>
    </div>
  `;
}

function ideaCard(lane, item) {
  const riskClass = `risk-${item.risk}`;
  const catalysts = (item.catalysts || []).slice(0,3).map(c=>`<li>${c}</li>`).join('');
  const thesis = item.thesis || item.whyInteresting || '';
  const id = `chart-${item.ticker}`;
  return `
    <div class="card" role="article">
      <div class="row">
        <div>
          <div class="ticker">${item.ticker}</div>
          <div class="name">${item.name || ''}</div>
        </div>
        <div class="badges">
          <span class="badge">${item.timeframe}</span>
          <span class="badge ${riskClass}">${item.risk}</span>
          <span class="badge">${pct(item.confidence)}%</span>
        </div>
      </div>
      <div class="conf ${lane}" aria-label="Confidence">
        <div class="fill" style="width:${pct(item.confidence)}%"></div>
      </div>
      <div>${thesis}</div>
      ${catalysts ? `<ul class="catalysts">${catalysts}</ul>` : ''}
      ${ideaActions(item.ticker, item.name || '')}
      <div class="compare-chart" id="${id}-wrap" style="display:none;">
        <canvas id="${id}" height="150"></canvas>
      </div>
    </div>
  `;
}

function render(json) {
  state.screen = json;
  $('summary').textContent = json.summary || '';
  $('buyList').innerHTML  = (json.buy  || []).map(i=>ideaCard('buy',i)).join('') || '<div class="card">No items</div>';
  $('holdList').innerHTML = (json.hold || []).map(i=>ideaCard('hold',i)).join('') || '<div class="card">No items</div>';
  $('sellList').innerHTML = (json.sell || []).map(i=>ideaCard('sell',i)).join('') || '<div class="card">No items</div>';
  $('utrList').innerHTML  = (json.underTheRadar || []).map(i=>ideaCard('buy',i)).join('') || '<div class="card">No ideas yet</div>';
  $('disclaimers').innerHTML = (json.disclaimers || []).map(d=>`• ${d}`).join(' ');

  // Wire per-card buttons
  document.querySelectorAll('.add-watch').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const t = btn.dataset.t, n = btn.dataset.n;
      if (!state.watchlist.includes(t)) state.watchlist.push(t);
      saveWatchlist(); btn.textContent = '✓ In Watchlist';
    });
  });
  document.querySelectorAll('.add-compare').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const t = btn.dataset.t;
      state.compareSet.add(t);
      openCompare();
      renderCompareList();
    });
  });
  document.querySelectorAll('.view-chart').forEach(btn=>{
    btn.addEventListener('click', ()=> toggleCardChart(btn.dataset.t));
  });
}

function rowsForCSV() {
  const j = state.screen || {};
  const rows = [['Lane','Ticker','Name','Timeframe','Confidence','Risk','Thesis/Cause','Catalysts']];
  [['Buy','buy'],['Hold','hold'],['Sell','sell']].forEach(([label,key])=>{
    (j[key]||[]).forEach(i=>{
      rows.push([label, i.ticker, i.name||'', i.timeframe, pct(i.confidence), i.risk, i.thesis||i.whyInteresting||'', (i.catalysts||[]).join(' | ')]);
    });
  });
  (j.underTheRadar||[]).forEach(i=>{
    rows.push(['UnderTheRadar', i.ticker, i.name||'', i.timeframe, pct(i.confidence), i.risk, i.whyInteresting||'', (i.catalysts||[]).join(' | ')]);
  });
  return rows;
}

// ---------- Charts ----------
function sma(values, win){
  const out=[]; let sum=0;
  values.forEach((v,i)=>{ sum+=v; if(i>=win) sum-=values[i-win]; out.push(i>=win-1 ? +(sum/win).toFixed(2) : null); });
  return out;
}
function rsi(values, period=14){
  let gains=0, losses=0; const rsis=[];
  for(let i=1;i<values.length;i++){
    const diff=values[i]-values[i-1];
    const gain=Math.max(0,diff), loss=Math.max(0,-diff);
    if(i<=period){ gains+=gain; losses+=loss; rsis.push(null); }
    else{
      gains=(gains*(period-1)+gain)/period;
      losses=(losses*(period-1)+loss)/period;
      const rs = losses===0 ? 100 : 100 - (100/(1+(gains/(losses||1e-9))));
      rsis.push(+rs.toFixed(2));
    }
  }
  rsis.unshift(null);
  return rsis;
}

async function drawChart(ticker, canvas){
  const data = await get(`/api/series?ticker=${encodeURIComponent(ticker)}&days=180`);
  const xs = data.series.map(p=>new Date(p.t));
  const closes = data.series.map(p=>p.close);
  const s20 = sma(closes,20), s50=sma(closes,50), r=rsi(closes,14);

  if (state.charts.get(ticker)) { state.charts.get(ticker).destroy(); state.charts.delete(ticker); }

  const ctx = canvas.getContext('2d');
  const chart = new Chart(ctx, {
    type:'line',
    data:{
      labels: xs,
      datasets:[
        { label:`${ticker} Close`, data:closes, yAxisID:'y', pointRadius:0, tension:.25 },
        { label:'SMA20', data:s20, yAxisID:'y', pointRadius:0, tension:.25 },
        { label:'SMA50', data:s50, yAxisID:'y', pointRadius:0, tension:.25 },
        { label:'RSI14', data:r, yAxisID:'y1', pointRadius:0, tension:.25 }
      ]
    },
    options:{
      scales:{
        x: { display:false },
        y: { position:'left', grid:{color:'#1e2a3b'} },
        y1:{ position:'right', min:0, max:100, ticks:{stepSize:20}, grid:{display:false} }
      },
      plugins:{ legend:{ labels:{ color:'#cde1f7' } } }
    }
  });
  state.charts.set(ticker, chart);
}

async function toggleCardChart(ticker){
  const wrap = $(`chart-${ticker}-wrap`);
  if (!wrap) return;
  const shown = wrap.style.display !== 'none';
  if (shown) {
    wrap.style.display = 'none';
    const ch = state.charts.get(ticker); if (ch){ ch.destroy(); state.charts.delete(ticker); }
  } else {
    wrap.style.display = 'block';
    const canvas = $(`chart-${ticker}`);
    await drawChart(ticker, canvas);
  }
}

// ---------- Compare Drawer ----------
function openCompare(){ $('compareDrawer').setAttribute('aria-hidden','false'); }
function closeCompare(){ $('compareDrawer').setAttribute('aria-hidden','true'); }
function renderCompareList(){
  const list = $('compareList');
  list.innerHTML = [...state.compareSet].map(t => `
    <div class="drawer-item">
      <strong>${t}</strong>
      <div>
        <button class="smallbtn analyze" data-t="${t}">Analyze</button>
        <button class="smallbtn remove" data-t="${t}">Remove</button>
      </div>
    </div>
  `).join('') || '<div class="drawer-item">Add tickers to compare.</div>';

  list.querySelectorAll('.remove').forEach(b=> b.onclick = ()=>{ state.compareSet.delete(b.dataset.t); renderCompareList(); });
  list.querySelectorAll('.analyze').forEach(b=> b.onclick = async ()=>{
    const json = await post('/api/analyze', { ticker: b.dataset.t });
    renderCompareResults(b.dataset.t, json);
  });
}
function renderCompareResults(label, json){
  const container = $('compareResults');
  const div = document.createElement('div');
  div.className = 'compare-card';
  const id = `cmp-${label}-chart`;
  div.innerHTML = `
    <div class="compare-head">
      <strong>${label}</strong>
      <button class="smallbtn" data-t="${label}">Chart</button>
    </div>
    <div>${json.summary || ''}</div>
    <div class="compare-chart" id="${id}-wrap" style="display:none;"><canvas id="${id}" height="140"></canvas></div>
  `;
  container.appendChild(div);

  div.querySelector('button').onclick = async ()=>{
    const wrap = $(`${id}-wrap`);
    const shown = wrap.style.display !== 'none';
    if (shown){ wrap.style.display='none'; }
    else { wrap.style.display='block'; await drawChart(label, $(`${id}`)); }
  };
}

// ---------- Watchlist Drawer ----------
function openWatch(){ $('watchDrawer').setAttribute('aria-hidden','false'); renderWatchlist(); }
function closeWatch(){ $('watchDrawer').setAttribute('aria-hidden','true'); }
function renderWatchlist(){
  const el = $('watchItems');
  el.innerHTML = state.watchlist.map(t => `
    <div class="drawer-item">
      <strong>${t}</strong>
      <div>
        <button class="smallbtn analyze" data-t="${t}">Analyze</button>
        <button class="smallbtn remove" data-t="${t}">Remove</button>
      </div>
    </div>
  `).join('') || '<div class="drawer-item">Your watchlist is empty.</div>';

  el.querySelectorAll('.remove').forEach(b=> b.onclick = ()=>{
    state.watchlist = state.watchlist.filter(x=>x!==b.dataset.t);
    saveWatchlist(); renderWatchlist();
  });
  el.querySelectorAll('.analyze').forEach(b=> b.onclick = async ()=>{
    const json = await post('/api/analyze', { ticker: b.dataset.t });
    render(json);
  });
}

// ---------- Events ----------
$('runBtn').addEventListener('click', async ()=>{
  const risk = $('risk').value;
  const region = $('region').value;
  $('summary').textContent = 'Running analysis…';
  const json = await post('/api/screen', { risk, region });
  render(json);
});
$('exportBtn').addEventListener('click', ()=>{
  if (!state.screen) { alert('Run analysis first.'); return; }
  downloadCSV(`tradesense_${new Date().toISOString().slice(0,10)}.csv`, rowsForCSV());
});

$('searchForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const raw = $('tickerInput').value.trim().toUpperCase();
  if (!/^[A-Z][A-Z0-9.\-]{0,9}$/.test(raw)) { alert('Enter a valid ticker (e.g., AAPL, BRK.B, RIO)'); return; }
  $('summary').textContent = `Analyzing ${raw}…`;
  const json = await post('/api/analyze', { ticker: raw });
  render(json);
});

$('compareOpenBtn').onclick = ()=> { openCompare(); renderCompareList(); };
$('compareCloseBtn').onclick = closeCompare;
$('watchOpenBtn').onclick = openWatch;
$('watchCloseBtn').onclick = closeWatch;

$('compareForm').addEventListener('submit', (e)=>{
  e.preventDefault();
  const t = $('compareInput').value.trim().toUpperCase();
  if (!/^[A-Z][A-Z0-9.\-]{0,9}$/.test(t)) { alert('Invalid ticker'); return; }
  state.compareSet.add(t); $('compareInput').value = '';
  renderCompareList();
});

// No auto-fetch on load (manual only)
