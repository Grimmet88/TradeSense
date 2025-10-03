import streamlit as st
from src.pipeline import main
from src.scraping import fetch_news

st.title("TradeSense Dashboard")

ranked, news_results, decisions = main()

st.header("Buy/Sell/Hold Signals")
if decisions:
    for ticker, info in decisions.items():
        st.write(
            f"{ticker}: **{info['action']}** "
            f"(Momentum: {info['momentum']:.2f}, Sentiment: {info['sentiment']:.2f})"
        )
else:
    st.write("No decisions available.")

st.header("Top Trading Candidates")
if ranked is not None and hasattr(ranked, "head") and not ranked.empty:
    st.write(ranked.head(5))
else:
    st.write("No ranked data available.")

st.header("Relevant News Headlines")
if news_results:
    for nr in news_results[:10]:
        st.markdown(f"**Tickers:** {', '.join(nr['tickers'])}")
        st.markdown(f"[{nr['title']}]({nr['link']})")
        st.markdown(f"Sentiment: `{nr['sentiment']:.2f}`")
        st.markdown("---")
else:
    st.info("No relevant news articles found.")

# --- DEBUG: Show all fetched news articles ---
st.header("All Fetched News (Debug)")
all_articles = fetch_news()
for a in all_articles[:20]:  # Show first 20 for brevity
    st.markdown(f"**{a['title']}** ([link]({a['link']}))")
    st.markdown(f"Summary: {a['summary']}")
    st.markdown("---")
