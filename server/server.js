// server/server.js
import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';
import crypto from 'crypto';
import path from 'path';
import { fileURLToPath } from 'url';
import { SYSTEM_PROMPT, makeScreenPrompt, makeSingleTickerPrompt } from './prompts.js';

// ---------------------------
// Env & constants
// ---------------------------
const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

const {
  GROQ_API_KEY,
  GROQ_BASE_URL = 'https://api.groq.com/openai/v1',
  GROQ_MODEL = 'llama-3.1-70b-versatile',
  PORT = 8787,
  MOCK_FALLBACK = 'true',

  // Series providers
  SERIES_PROVIDER = 'yahoo', // yahoo | alphavantage | polygon
  POLYGON_API_KEY,
  ALPHAVANTAGE_API_KEY,
  SERIES_CACHE_TTL = '900', // seconds
} = process.env;

const TICKER_RE = /^[A-Z][A-Z0-9.\-]{0,9}$/;

// Resolve /web directory robustly
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const WEB_DIR = path.join(__dirname, '..', 'web');

// ---------------------------
// Helpers
// ---------------------------
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
    throw new Error(`Groq ${res.status}: ${text}`);
  }

  const data = await res.json();
  const content = data?.choices?.[0]?.message?.content ?? '{}';
  return JSON.parse(content);
}

// Simple mocks if GROQ fails and MOCK_FALLBACK=true
const MOCK = {
  summary:
    'Mixed risk-on tone; mega-cap tech consolidating while cyclicals bid.',
  buy: [
    {
      ticker: 'XOM',
      name: 'Exxon Mobil',
      thesis:
        'Cash flow support + dividend; energy demand resilience.',
      timeframe: 'medium',
      confidence: 82,
      risk: 'medium',
      catalysts: ['OPEC supply signals', 'Refining margins'],
    },
    {
      ticker: 'AMD',
      name: 'Advanced Micro Devices',
      thesis: 'AI GPU/CPU share gains vs peers.',
      timeframe: 'medium',
      confidence: 76,
      risk: 'medium',
      catalysts: ['MI-series uptake', 'Earnings guide'],
    },
  ],
  hold: [
    {
      ticker: 'NVDA',
      name: 'NVIDIA',
      thesis: 'Leader in AI, valuation rich; watch digestion.',
      timeframe: 'short',
      confidence: 74,
      risk: 'medium',
      catalysts: ['Data center demand', 'New product cadence'],
    },
  ],
  sell: [
    {
      ticker: 'RIVN',
      name: 'Rivian',
      thesis:
        'Cash burn + competition; path to profitability unclear.',
      timeframe: 'short',
      confidence: 70,
      risk: 'high',
      catalysts: ['Deliveries', 'Gross margin trend'],
    },
  ],
  underTheRadar: [
    {
      ticker: 'INMD',
      name: 'InMode',
      whyInteresting:
        'High-margin medtech with new platform cycle.',
      timeframe: 'medium',
      confidence: 65,
      risk: 'medium',
      catalysts: ['Reg approvals', 'Intl expansion'],
    },
    {
      ticker: 'ASO',
      name: 'Academy Sports + Outdoors',
      whyInteresting: 'Omnichannel retail; resilient cash flows.',
      timeframe: 'medium',
      confidence: 63,
      risk: 'medium',
      catalysts: ['Comp sales', 'New stores'],
    },
  ],
  disclaimers: [
    'This is not financial advice.',
    'Do your own research.',
  ],
};

// ---------------------------
// GROQ-backed endpoints
// ---------------------------
app.post('/api/screen', async (req, res) => {
  const { risk = 'medium', region = 'US' } = req.body || {};
  try {
    const json = await groqJSON([
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: makeScreenPrompt({ risk, region }) },
    ]);
    res.json(json);
  } catch (err) {
    console.error('[screen]', err.message);
    if (String(MOCK_FALLBACK).toLowerCase() === 'true') return res.json(MOCK);
    res.status(500).json({ error: 'Model error' });
  }
});

app.post('/api/analyze', async (req, res) => {
  try {
    const ticker = String(req.body?.ticker || '').toUpperCase().trim();
    if (!TICKER_RE.test(ticker)) {
      return res
        .status(400)
        .json({
          error:
            'Provide a valid ticker (e.g., AAPL, BRK.B, RIO).',
        });
    }
    const json = await groqJSON([
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: makeSingleTickerPrompt(ticker) },
    ]);
    res.json(json);
  } catch (err) {
    console.error('[analyze]', err.message);
    if (String(MOCK_FALLBACK).toLowerCase() === 'true') return res.json(MOCK);
    res.status(500).json({ error: 'Model error' });
  }
});

// ---------------------------
// Real price series providers
// ---------------------------

// Cache for series responses: key -> {expires, data}
const seriesCache = new Map();
function cacheGet(key) {
  const hit = seriesCache.get(key);
  if (!hit) return null;
  if (Date.now() > hit.expires) {
    seriesCache.delete(key);
    return null;
  }
  return hit.data;
}
function cacheSet(key, data, ttlSec) {
  seriesCache.set(key, {
    expires: Date.now() + ttlSec * 1000,
    data,
  });
}
function toSeries(ticker, rows) {
  return {
    ticker,
    series: rows
      .filter(
        (r) => Number.isFinite(r.close) && Number.isFinite(r.t),
      )
      .sort((a, b) => a.t - b.t),
  };
}

// Provider: Yahoo (no key)
async function fetchSeriesYahoo(ticker, days) {
  const range =
    days <= 30 ? '1mo' : days <= 90 ? '3mo' : days <= 180 ? '6mo' : '1y';
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(
    ticker,
  )}?range=${range}&interval=1d&includePrePost=false`;
  const res = await fetch(url, {
    headers: { 'User-Agent': 'TradeSense/1.0' },
  });
  if (!res.ok) throw new Error(`Yahoo ${res.status}`);
  const j = await res.json();
  const r = j?.chart?.result?.[0];
  const ts = r?.timestamp || [];
  const closes = r?.indicators?.quote?.[0]?.close || [];
  const rows = ts.map((t, i) => ({
    t: (t * 1000) | 0,
    close: Number(closes[i]),
  }));
  return toSeries(ticker, rows.slice(-days));
}

// Provider: Alpha Vantage (free key; rate limited)
async function fetchSeriesAlphaVantage(ticker, days) {
  if (!ALPHAVANTAGE_API_KEY)
    throw new Error('Missing ALPHAVANTAGE_API_KEY');
  const url = `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=${encodeURIComponent(
    ticker,
  )}&outputsize=compact&apikey=${ALPHAVANTAGE_API_KEY}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`AlphaVantage ${res.status}`);
  const j = await res.json();
  const series = j['Time Series (Daily)'];
  if (!series) throw new Error('AlphaVantage: no data');
  const rows = Object.entries(series)
    .map(([date, o]) => ({
      t: new Date(date + 'T16:00:00Z').getTime(),
      close: Number(o['5. adjusted close']),
    }))
    .sort((a, b) => a.t - b.t)
    .slice(-days);
  return toSeries(ticker, rows);
}

// Provider: Polygon (paid/free trial)
async function fetchSeriesPolygon(ticker, days) {
  if (!POLYGON_API_KEY) throw new Error('Missing POLYGON_API_KEY');
  const end = new Date();
  const start = new Date(end.getTime() - (days + 5) * 24 * 3600 * 1000); // buffer for weekends/holidays
  const fmt = (d) => d.toISOString().slice(0, 10);
  const url = `https://api.polygon.io/v2/aggs/ticker/${encodeURIComponent(
    ticker,
  )}/range/1/day/${fmt(start)}/${fmt(end)}?adjusted=true&sort=asc&limit=50000&apiKey=${POLYGON_API_KEY}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Polygon ${res.status}`);
  const j = await res.json();
  const rows = (j?.results || [])
    .map((bar) => ({ t: Number(bar.t), close: Number(bar.c) }))
    .slice(-days);
  return toSeries(ticker, rows);
}

// Optional lightweight rate limiter per ticker
const lastHit = new Map(); // ticker -> timestamp
function rateLimitMs(ms = 15000) {
  return (req, res, next) => {
    const tkr = String(req.query.ticker || '').toUpperCase();
    const now = Date.now();
    const prev = lastHit.get(tkr) || 0;
    if (tkr && now - prev < ms) {
      return res
        .status(429)
        .json({
          error:
            'Too many requests for this ticker. Try again shortly.',
        });
    }
    lastHit.set(tkr, now);
    next();
  };
}

// /api/series with provider switch + cache
app.get('/api/series', rateLimitMs(10000), async (req, res) => {
  try {
    const ticker = String(req.query.ticker || '').toUpperCase();
    const days = Math.max(30, Math.min(365, Number(req.query.days || 180)));
    if (!TICKER_RE.test(ticker)) {
      return res.status(400).json({ error: 'Invalid ticker' });
    }

    const key = crypto
      .createHash('md5')
      .update(`${SERIES_PROVIDER}|${ticker}|${days}`)
      .digest('hex');

    const cached = cacheGet(key);
    if (cached) return res.json(cached);

    let out;
    if (SERIES_PROVIDER === 'polygon') {
      out = await fetchSeriesPolygon(ticker, days);
    } else if (SERIES_PROVIDER === 'alphavantage') {
      out = await fetchSeriesAlphaVantage(ticker, days);
    } else {
      out = await fetchSeriesYahoo(ticker, days); // default
    }

    cacheSet(key, out, Number(SERIES_CACHE_TTL) || 900);
    res.json(out);
  } catch (e) {
    console.error('[series]', e.message);
    res
      .status(502)
      .json({ error: 'Series provider failed', detail: e.message });
  }
});

// ---------------------------
// Health & static hosting
// ---------------------------
app.get('/health', (req, res) => res.json({ ok: true }));

// Serve static frontend from /web
app.use('/', express.static(WEB_DIR));

// ---------------------------
// Start server
// ---------------------------
app.listen(Number(PORT), () => {
  console.log(`TradeSense backend → http://localhost:${PORT}`);
});
