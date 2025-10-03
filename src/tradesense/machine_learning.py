import math

class Model:
    def _last_row(self, df):
        """Return the last NON-NaN row as a dict of scalars."""
        tail = df.dropna().iloc[-1:]
        return {
            "rsi14": float(tail["rsi14"].values[0]),
            "sma20": float(tail["sma20"].values[0]),
            "sma50": float(tail["sma50"].values[0]),
            "date":  str(tail.index[-1].date()),
        }

    def score(self, df):
        # Extract clean scalars (avoid Series-in-if errors)
        vals = self._last_row(df)
        rsi = vals["rsi14"]
        sma20 = vals["sma20"]
        sma50 = vals["sma50"]

        # Default
        signal = "hold"
        confidence = 0.5

        # Guard against NaN
        if any(math.isnan(x) for x in (rsi, sma20, sma50)):
            return {
                "signal": signal,
                "confidence": confidence,
                "latest_date": vals["date"],
                "indicators": {"rsi14": rsi, "sma20": sma20, "sma50": sma50},
                "reason": "NaN indicators; holding",
            }

        # Simple rules
        if (rsi < 35) and (sma20 > sma50):
            signal, confidence = "buy", 0.7
        elif (rsi > 65) and (sma20 < sma50):
            signal, confidence = "sell", 0.7
        else:
            signal, confidence = "hold", 0.55

        return {
            "signal": signal,
            "confidence": float(confidence),
            "latest_date": vals["date"],
            "indicators": {"rsi14": rsi, "sma20": sma20, "sma50": sma50},
        }

