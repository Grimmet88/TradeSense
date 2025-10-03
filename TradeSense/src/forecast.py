def get_momentum_score(prices):
    # Simple momentum: last price minus mean
    return prices.iloc[-1] - prices.mean()
