COMPANY_MAP = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOG": "Google",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "NFLX": "Netflix",
    "NVDA": "Nvidia",
    "META": "Meta",
    "JPM": "JPMorgan",
    "V": "Visa"
}

def get_action(momentum, sentiment):
    # Basic rule-based decision
    if momentum > 2 and sentiment > 0.1:
        return "Buy"
    elif momentum < -2 and sentiment < -0.1:
        return "Sell"
    else:
        return "Hold"

def mentions_ticker(article, tickers):
    mentioned = []
    text = (article.get("title", "") + " " + article.get("summary", "")).upper()
    for t in tickers:
        company = COMPANY_MAP.get(t, "")
        if t.upper() in text or company.upper() in text:
            mentioned.append(t)
    return mentioned
