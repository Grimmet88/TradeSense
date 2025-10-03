from tradesense.pipeline import Pipeline
import json

if __name__ == "__main__":
    # choose tickers you want to test
    p = Pipeline(tickers=["AAPL", "NVDA", "SPY"])
    results = p.run()
    # print nicely as JSON
    print(json.dumps(results, indent=2))

