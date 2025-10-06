// server/server.js
// ---------------- Environment load (from /server/.env) ----------------
import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';
import crypto from 'crypto';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { XMLParser } from 'fast-xml-parser';
import { SYSTEM_PROMPT, makeScreenPrompt, makeSingleTickerPrompt } from './prompts.js';

// Resolve paths for ESM and load env from /server/.env
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '.env') });

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

// ---------------- Config ----------------
const {
  // Groq
  GROQ_API_KEY,
  GROQ_BASE_URL = 'https://api.groq.com/openai/v1',
  GROQ_MODEL = 'llama-3.1-70b-instruct', // <- supported default
  MOCK_FALLBACK = 'true',

  // Server
  PORT = 8787,

  // Series providers
  SERIES_PROVIDER = 'yahoo',            // yahoo | alphavantage | polygon
  POLYGON_API_KEY,
  ALPHAVANTAGE_API_KEY,
  SERIES_CACHE_TTL = '900',             // seconds

  // News cache
  NEWS_CACHE_TTL = '300',               // seconds
} = process.env;

console.log('GROQ key loaded?', GROQ_API_KEY ? 'yes' : 'NO (mock fallback may trigger)');

const WEB_DIR = path.join(__dirname, '..', 'web');
const TICKER_RE = /^[A-Z][A-Z0-9.\-]{0,9}$/;

// ---------------- Helpers ----------------
async function groqJSON(messages) {
  if (!GROQ_API_KEY) throw new Error('Missing GROQ_API_KEY');
  const res = await fetch(`${GROQ_BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${GROQ_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: GROQ_MODEL,
      temperature: 0.3,
      response_format: { type: 'json_object' },
      messages,
    }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    if (text.includes('model_decommissioned')) {
      throw new Error(
        `Groq says model is decommissioned. Set GROQ_MODEL in server/.env to a supported model. Raw: ${text}`
      );
    }
    throw new Error(`Groq ${res.status}: ${text}`);
  }
  const data = await res.json();
  const content = data?.choices?.[0]?.message?.content ?? '{}';
  return JSON.parse(content);
}

// Mock payload for UX continuity when GROQ fails
const MOCK = {
  summary: 'Mixed risk-on tone; mega-cap tech consolidating while cyclicals bid.',
  buy: [
    { ticker: 'XOM', name: 'Exxon Mobil', thesis: 'Cash flow + dividend; energy demand resilience.', timeframe: 'medium', confidence: 82, risk: 'medium', catalysts: ['OPEC supply signals','Refining margins'] },
    { ticker: 'AMD', name: 'Advanced Micro Devices', thesis: 'AI GPU/CPU share gains vs peers.', timeframe: 'medium', confidence: 76, risk: 'medium', catalysts: ['MI-series uptake','Earnings guide'] }
  ],
  hold: [
    { ticker: 'NVDA', name: 'NVIDIA', thesis: 'Leader in AI, valuation rich; watch digestion.', timeframe: 'short', confidence: 74, risk: 'medium', catalysts: ['Data center demand','New product cadence'] }
  ],
  sell: [
    { ticker: 'RIVN', name: 'Rivian', thesis: 'Cash burn + competition; path to profitability unclear.', timeframe: 'short', confidence: 70, risk: 'high', catalysts: ['Deliveries','Gross margin trend'] }
  ],
  underTheRadar: [
    { ticker: 'INMD', name: 'InMode', whyInteresting: 'High-margin medtech with new platform cycle.', timeframe: 'medium', confidence: 65, risk: 'medium', catalysts: ['Reg approvals','Intl expansion'] },
    { ticker: 'ASO', name: 'Academy Sports + Outdoors', whyInteresting: 'Omnichannel retail; resilient cash flows.', timeframe: 'medium', confidence: 63, risk: 'medium', catalysts: ['Comp sales','New stores'] }
  ],
  disclaimers: ['This is not financial advice.', 'Do your own research.']
};

// Add explicit mock flag to responses so UI can show/hide the badge deterministically
function withMockFlag(payload, isMock) {
  try { return { ...payload, mock: !!isMock }; }
  catch { return { mock: !!isMock }; }
}

// ---------------- GROQ-backed endpoints ----------------
app.post('/api/screen', async (req, res) => {
  const { risk = 'medium', region = 'US' } = req.body || {};
  try {
    const json = await groqJSON([
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: makeScreenPrompt({ risk, region }) },
    ]);
    return res.json(withMockFlag(json, false));
  } catch (err) {
    console.error('[screen]', err.message);
    if (String(MOCK_FALLBACK).toLowerCase() === 'true') {
      return res.json(withMockFlag(MOCK, true));
    }
    return res.status(500).json({ error: 'Model error' });
  }
});

app.post('/api/analyze', async (req, res) => {
  try {
    const ticker = String(req.body?.ticker || '').toUpperCase().trim();
    if (!TICKER_RE.test(ticker)) {
      return res.status(400).json({ error: 'Provide a valid ticker (e.g., AAPL, BRK.B, RIO).' });
    }
    const json = await groqJSON([
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: makeSingleTickerPrompt(ticker) },
    ]);
    return res.json(withMockFlag(json, false));
  } catch (err) {
    console.error('[analyze]', err.message);
    if (String(MOCK_FALLBACK).toLowerCase() === 'true') {
      return res.json(withMockFlag(MOCK, true));
    }
    return res.status(500).json({ error: 'Model error' });
  }
});

// ---------------- Price series providers ----------------
function toSeries(ticker, rows) {
  return {
    ticker,
    series: rows
      .filter(r => Number.isFinite(r.close) && Number.isFinite(r.t))
      .sort((a, b) => a.t - b.t),
  };
}

// Yahoo (no key)
async function fetchSeriesYahoo(ticker, days) {
  const range = days <= 30 ? '1mo' : days <= 90 ? '3mo' : days <= 180 ? '6mo' : '1y';
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=${range}&interval=1d&includePrePost=false`;
  const res = await fetch(url, { headers: { 'User-Agent': 'TradeSense/1.0' } });
  if (!res.ok) throw new Error(`Yahoo ${res.status}`);
  const j = await res.json();
  const r = j?.chart?.result?.[0];
  const ts = r?.timestamp || [];
  const closes = r?.indicators?.quote?.[0]?.close || [];
  const rows = ts.map((t, i) => ({ t: (t * 1000) | 0, close: Number(closes[i]) }));
  return toSeries(ticker, rows.slice(-days));
}

// Alpha Vantage (free key; rate-limited)
async function fetchSeriesAlphaVantage(ticker, days) {
  if (!ALPHAVANTAGE_API_KEY) throw new Error('Missing ALPHAVANTAGE_API_KEY');
  const url = `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=${encodeURIComponent(ticker)}&outputsize=compact&apikey=${ALPHAVANTAGE_API_KEY}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`AlphaVantage ${res.status}`);
  const j = await res.json();
  const series = j['Time Series (Daily)'];
  if (!series) throw new Error('AlphaVantage: no data');
  const rows = Object.entries(series)
    .map(([date, o]) => ({ t: new Date(date + 'T16:00:00Z').getTime(), close: Number(o['5. adjusted close']) }))
    .sort((a, b) => a.t - b.t)
    .slice(-days);
  return toSeries(ticker, rows);
}

// Polygon (paid/free trial)
async function fetchSeriesPolygon(ticker, days) {
  if (!POLYGON_API_KEY) throw new Error('Missing POLYGON_API_KEY');
  const end = new Date();
  const start = new Date(end.getTime() - (days + 5) * 24 * 3600 * 1000); // buffer for weekends/holidays
  const fmt = (d) => d.toISOString().slice(0, 10);
  const url = `https://api.polygon.io/v2/aggs/ticker/${encodeURIComponent(ticker)}/range/1/day/${fmt(start)}/${fmt(end)}?adjusted=true&sort=asc&limit=50000&apiKey=${POLYGON_API_KEY}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Polygon ${res.status}`);
  const j = await res.json();
  const rows = (j?.results || []).map(bar => ({ t: Number(bar.t), close: Number(bar.c) })).slice(-days);
  return toSeries(ticker, rows);
}

// Cache + lightweight rate limiter
const seriesCache = new Map(); // key -> {expires, data}
const lastHit = new Map();     // ticker -> timestamp
function cacheGet(key) { const v = seriesCache.get(key); if (!v) return null; if (Date.now() > v.expires) { seriesCache.delete(key); return null; } return v.data; }
function cacheSet(key, data, ttl) { seriesCache.set(key, { expires: Date.now() + (ttl * 1000), data }); }
function rateLimitMs(ms = 10000) {
  return (req, res, next) => {
    const tkr = String(req.query.ticker || '').toUpperCase();
    const now = Date.now();
    const prev = lastHit.get(tkr) || 0;
    if (tkr && now - prev < ms) return res.status(429).json({ error: 'Too many requests for this ticker. Try again shortly.' });
    lastHit.set(tkr, now);
    next();
  };
}

// /api/series (real data)
app.get('/api/series', rateLimitMs(10000), async (req, res) => {
  try {
    const ticker = String(req.query.ticker || '').toUpperCase();
    const days = Math.max(30, Math.min(365, Number(req.query.days || 180)));
    if (!TICKER_RE.test(ticker)) return res.status(400).json({ error: 'Invalid ticker' });

    const key = crypto.createHash('md5').update(`${SERIES_PROVIDER}|${ticker}|${days}`).digest('hex');
    const cached = cacheGet(key);
    if (cached) return res.json(cached);

    let out;
    if (SERIES_PROVIDER === 'polygon') out = await fetchSeriesPolygon(ticker, days);
    else if (SERIES_PROVIDER === 'alphavantage') out = await fetchSeriesAlphaVantage(ticker, days);
    else out = await fetchSeriesYahoo(ticker, days); // default

    cacheSet(key, out, Number(SERIES_CACHE_TTL) || 900);
    res.json(out);
  } catch (e) {
    console.error('[series]', e.message);
    res.status(502).json({ error: 'Series provider failed', detail: e.message });
  }
});

// ---------------- News (RSS) with small cache ----------------
const NEWS_SOURCES = [
  { name: 'Reuters Business', url: 'https://feeds.reuters.com/reuters/businessNews' },
  { name: 'CNBC Markets',    url: 'https://www.cnbc.com/id/100003114/device/rss/rss.html' },
  { name: 'Yahoo Finance',   url: 'https://finance.yahoo.com/news/rssindex' },
];

const xmlParser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '@_' });
function pickImageFromItem(item) {
  const media = item['media:content'] || item['media:thumbnail'];
  if (media && media['@_url']) return media['@_url'];
  if (Array.isArray(media) && media[0]?.['@_url']) return media[0]['@_url'];
  if (item.enclosure && item.enclosure['@_url']) return item.enclosure['@_url'];
  return '/news-placeholder.png';
}
function domainFromLink(link = '') { try { return new URL(link).hostname.replace(/^www\./,''); } catch { return ''; } }
async function fetchOneRss({ name, url }) {
  const res = await fetch(url, { headers: { 'User-Agent': 'TradeSense/1.0' } });
  if (!res.ok) throw new Error(`RSS ${name} ${res.status}`);
  const xml = await res.text();
  const j = xmlParser.parse(xml);
  const channel = j?.rss?.channel || j?.feed;
  const items = channel?.item || channel?.entry || [];
  return (Array.isArray(items) ? items : [items]).map(it => {
    const link = it.link?.href || it.link || it.guid || '';
    const title = it.title?._text || it.title || '';
    const desc = it.description?._text || it.description || it.summary || '';
    const pub = it.pubDate || it.published || it.updated || null;
    return {
      source: name,
      title: String(title).trim(),
      description: String(desc).replace(/<[^>]+>/g,'').trim(),
      link: typeof link === 'string' ? link : (link?.['#text'] || ''),
      publishedAt: pub ? new Date(pub).getTime() : Date.now(),
      image: pickImageFromItem(it),
      domain: '' // fill next
    };
  }).map(x => ({ ...x, domain: domainFromLink(x.link) }));
}
function dedupeByLink(items) {
  const seen = new Set();
  return items.filter(i => {
    if (!i.link || seen.has(i.link)) return false;
    seen.add(i.link);
    return true;
  });
}
// Tiny cache
const newsCache = new Map(); // key -> {expires, data}
function newsCacheGet(key){ const v=newsCache.get(key); if(!v) return null; if(Date.now()>v.expires){newsCache.delete(key); return null;} return v.data; }
function newsCacheSet(key,data,ttl){ newsCache.set(key,{expires:Date.now()+ttl*1000,data}); }

// GET /api/news?limit=18&q=optional
app.get('/api/news', async (req, res) => {
  const limit = Math.max(6, Math.min(50, Number(req.query.limit || 18)));
  const q = String(req.query.q || '').toLowerCase().trim();
  const cacheKey = JSON.stringify({ limit, q });

  const cached = newsCacheGet(cacheKey);
  if (cached) return res.json(cached);

  try {
    const all = (await Promise.allSettled(NEWS_SOURCES.map(fetchOneRss)))
      .flatMap(r => r.status === 'fulfilled' ? r.value : []);
    let news = dedupeByLink(all).sort((a,b) => b.publishedAt - a.publishedAt);

    if (q) {
      news = news.filter(n =>
        n.title.toLowerCase().includes(q) ||
        n.description.toLowerCase().includes(q) ||
        n.source.toLowerCase().includes(q) ||
        n.domain.toLowerCase().includes(q)
      );
    }

    const payload = { items: news.slice(0, limit) };
    newsCacheSet(cacheKey, payload, Number(NEWS_CACHE_TTL) || 300);
    res.json(payload);
  } catch (e) {
    console.error('[news]', e.message);
    res.status(502).json({ error: 'News fetch failed', detail: e.message });
  }
});

// ---------------- Health & static hosting ----------------
app.get('/health', (req, res) => res.json({ ok: true }));
app.use('/', express.static(WEB_DIR));

// ---------------- Start ----------------
app.listen(Number(PORT), () => {
  console.log(`TradeSense backend → http://localhost:${PORT}`);
});
