# TradeSense

TradeSense is a stock analysis web application that provides market news, screens stocks based on risk and region, analyzes individual tickers, and allows users to compare stocks and manage a watchlist. It leverages a Groq-backed reasoning API for market insights and real-time price series data.

## Features

- **Market News Landing Page:** Displays finance headlines with images, captions, sources, and links.
- **Trade Analysis Page:**
    - Market screening (Buy/Hold/Sell lanes + Under-the-Radar).
    - Single ticker analysis with detailed insights.
    - Confidence bars for each investment idea.
    - Sparkline charts (180-day) for tickers.
    - Right sidebar with stock comparison tool and persistent watchlist.
    - "Offline (mock data)" badge displayed when the backend is serving mock data.
- **Robust Backend:**
    - Groq chat-completions for AI-powered market analysis (JSON output).
    - Integrates with Yahoo Finance (default), AlphaVantage, and Polygon for price series.
    - RSS news aggregator from Reuters Business, CNBC Markets, and Yahoo Finance.
    - In-memory caching with TTL for price series and news.
    - Deterministic mock flag for UI feedback.

## Repository Layout
