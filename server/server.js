console.log('[TradeSense] server.js loaded');
import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';
import { SYSTEM_PROMPT, makeScreenPrompt, makeSingleTickerPrompt } from './prompts.js';

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

const {
  GROQ_API_KEY,
  GROQ_BASE_URL = 'https://api.groq.com/openai/v1',
  GROQ_MODEL = 'llama-3.1-70b-versatile',
  PORT = 8787,
  MOCK_FALLBACK = 'true'
} = process.env;

const TICKER_RE = /^[A-Z][A-Z0-9.\-]{0,9}$/;

// Simple mock to keep UI usable if the model call fails
const MOCK = {
  summary: "Mixed risk-on tone; mega-cap tech consolidating while cyclicals bid.",
  buy: [
    { ticker:"XOM", name:"Exxon Mobil", thesis:"Cash flow support + dividend; energy demand resilience.", timeframe:"medium", confidence:82, risk:"medium", catalysts:["OPEC supply signals","Refining margins"] },
    { ticker:"AMD", name:"Advanced Micro Devices", thesis:"AI GPU/CPU share gains vs peers.", timeframe:"medium", confidence:76, risk:"medium", catalysts:["MI-series uptake","Earnings guide"] }
  ],
  hold: [
    { ticker:"NVDA", name:"NVIDIA", thesis:"Leader in AI, valuation rich; watch digestion.", timeframe:"short", confidence:74, risk:"medium", catalysts:["Data center demand","New product cadence"] }
  ],
  sell: [
    { ticker:"RIVN", name:"Rivian", thesis:"Cash burn + competition; path to profitability unclear.", timeframe:"short", confidence:70, risk:"high", catalysts:["Deliveries","Gross margin trend"] }
  ],
  underTheRadar: [
    { ticker:"INMD", name:"InMode", whyInteresting:"High-margin medtech with new platform cycle.", timeframe:"medium", confidence:65, risk:"medium", catalysts:["Reg approvals","Intl expansion"] },
    { ticker:"ASO", name:"Academy Sports + Outdoors", whyInteresting:"Omnichannel retail; resilient cash flows.", timeframe:"medium", confidence:63, risk:"medium", catalysts:["Comp sales","New stores"] }
  ],
  disclaimers: ["This is not financial advice.", "Do your own research."]
};

async function groqJSON(messages) {
  if (!GROQ_API_KEY) throw new Error('Missing GROQ_API_KEY');
  const res = await fetch(`${GROQ_BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GROQ_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: GROQ_MODEL,
      temperature: 0.3,
      response_format: { type: "json_object" },
      messages
    })
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Groq ${res.status}: ${text}`);
  }

  const data = await res.json();
  const content = data?.choices?.[0]?.message?.content ?? '{}';
  return JSON.parse(content);
}

// POST /api/screen  -> full screen for Buy/Hold/Sell + underTheRadar
app.post('/api/screen', async (req, res) => {
  const { risk = 'medium', region = 'US' } = req.body || {};
  try {
    const json = await groqJSON([
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: makeScreenPrompt({ risk, region }) }
    ]);
    return res.json(json);
  } catch (err) {
    console.error('[screen]', err.message);
    if (String(MOCK_FALLBACK).toLowerCase() === 'true') return res.json(MOCK);
    return res.status(500).json({ error: 'Model error' });
  }
});

// POST /api/analyze -> single ticker analysis (same JSON schema)
app.post('/api/analyze', async (req, res) => {
  try {
    const ticker = String(req.body?.ticker || '').toUpperCase().trim();
    if (!TICKER_RE.test(ticker)) {
      return res.status(400).json({ error: 'Provide a valid ticker (e.g., AAPL, BRK.B, RIO).' });
    }
    const json = await groqJSON([
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: makeSingleTickerPrompt(ticker) }
    ]);
    return res.json(json);
  } catch (err) {
    console.error('[analyze]', err.message);
    if (String(MOCK_FALLBACK).toLowerCase() === 'true') return res.json(MOCK);
    return res.status(500).json({ error: 'Model error' });
  }
});

// --- Price series endpoint (mock today; swap to real provider later) ---
// GET /api/series?ticker=NVDA&days=180
app.get('/api/series', async (req, res) => {
  const ticker = String(req.query.ticker || '').toUpperCase();
  const days = Math.max(30, Math.min(365, Number(req.query.days || 180)));
  if (!/^[A-Z][A-Z0-9.\-]{0,9}$/.test(ticker)) {
    return res.status(400).json({ error: 'Invalid ticker' });
  }

  // TODO: connect to a real provider later (Polygon/Alpha Vantage/Yahoo)
  const now = Date.now();
  const oneDay = 24 * 3600 * 1000;
  const base = 100 + Math.random() * 50;
  const series = Array.from({ length: days }, (_, i) => {
    const t = now - (days - 1 - i) * oneDay;
    const drift = Math.sin(i / 9) * 2 + Math.cos(i / 21) * 1.5;
    const noise = (Math.random() - 0.5) * 1.2;
    const close = +(base + i * 0.15 + drift + noise).toFixed(2);
    return { t, close };
  });

  res.json({ ticker, series });
});

// Serve static frontend from /web
app.use('/', express.static('web'));

app.listen(Number(PORT), () => {
  console.log(`TradeSense backend → http://localhost:${PORT}`);
});
