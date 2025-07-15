
import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import altair as alt

st.set_page_config(page_title="🧠 Meme Coin Radar v5.2", layout="wide")
st.title("🧠 Meme Coin Radar v5.2")
st.markdown("Now using DexScreener for meme coins and CoinGecko for trending cryptos.")

# Sidebar - settings
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh Rate (mins)", 5, 60, 30)
view_mode = st.sidebar.selectbox("🔀 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
manual_refresh = st.sidebar.button("🔄 Refresh Now")

DEXSCREENER_PAIRS = {
    "PEPE": "ethereum/0x6982508145454ce325ddbe47a25d4ec3d2311933",
    "DOGE": "ethereum/0xba2ae424d960c26247dd6c32edc70b295c744c43",
    "SHIB": "ethereum/0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
    "FLOKI": "ethereum/0xfb5c6815ca3ac72ce9f5006869ae67f18bf77006",
    "WIF": "solana/6Z6gYz65ALzUK4tGkEq1NWBGTTycE9tf6Z9qs1DFKrgv",
    "BONK": "solana/DezXzFJgmXarh9FzfbxDPD1C7vKZ5bjrJVd9ESGZc4FQ",
    "TURBO": "ethereum/0xa5f2211b9b8170f694421f2046281775e8468043",
    "LADYS": "ethereum/0x12970e6868f88f6557b76120662c1b3e50a646bf",
    "HOPPY": "ethereum/0xcb2cc7ecc09d3f2fc525f4b8c073d043d5b59e5f",
    "COQ": "avalanche/0xb3b1f1e5a776a4a7e0068b9f6ef80d6d4feee528"
}

# Utility Functions
def format_price(p):
    if p is None:
        return "N/A"
    elif p >= 0.01:
        return f"${p:,.4f}"
    elif p >= 0.0001:
        return f"${p:,.6f}"
    else:
        return f"${p:.10f}".rstrip("0")

def get_dexscreener_data(pair):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{pair}"
        r = requests.get(url)
        d = r.json().get("pair", {})
        return {
            "symbol": d.get("baseToken", {}).get("symbol", "???"),
            "priceUsd": float(d.get("priceUsd", 0)),
            "priceChange": float(d.get("priceChange", 0)),
            "volume24h": float(d.get("volume", 0)),
            "sparkline": d.get("priceChart", [])
        }
    except:
        return {"symbol": "???", "priceUsd": None, "priceChange": 0, "volume24h": 0, "sparkline": []}

def get_top_hot_cryptos(limit=10):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    try:
        response = requests.get(url, params={"vs_currency": "usd", "order": "percent_change_24h_desc", "per_page": 500, "page": 1})
        top = []
        for coin in response.json():
            if coin['price_change_percentage_24h'] and coin['price_change_percentage_24h'] > 3:
                top.append({
                    "name": coin['name'],
                    "price": coin['current_price'],
                    "change": coin['price_change_percentage_24h'],
                    "volume": coin['total_volume']
                })
        return sorted(top, key=lambda x: x['change'], reverse=True)[:limit]
    except:
        return []

# Manual and auto refresh logic
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

if should_refresh:
    st.session_state.last_refresh = now

    st.markdown(f"⏱️ **Last Refreshed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if view_mode == "🐸 Meme Coins":
        st.subheader("📊 Meme Coins (via DexScreener)")

        for name, pair in DEXSCREENER_PAIRS.items():
            data = get_dexscreener_data(pair)
            price = data['priceUsd']
            sparkline = data['sparkline']
            with st.expander(f"{name} — {format_price(price)} ({data['priceChange']}%)", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Price:** {format_price(price)}")
                    st.write(f"**24h Change:** {data['priceChange']}%")
                    st.write(f"**Volume:** ${data['volume24h']:,.0f}")
                with col2:
                    if sparkline:
                        df = pd.DataFrame({
                            "point": list(range(len(sparkline))),
                            "price": [float(p) for p in sparkline]
                        })
                        chart = alt.Chart(df).mark_line().encode(x="point", y="price").properties(height=100)
                        st.altair_chart(chart, use_container_width=True)

    elif view_mode == "💰 Hot Cryptos":
        st.subheader("🔥 Top Trending Cryptos")
        hot_cryptos = get_top_hot_cryptos()
        if hot_cryptos:
            for coin in hot_cryptos:
                with st.expander(f"{coin['name']} — +{coin['change']:.2f}%", expanded=True):
                    st.write(f"**Price:** {format_price(coin['price'])}")
                    st.write(f"**24h Volume:** ${coin['volume']:,.0f}")
        else:
            st.info("No hot cryptos found at this time.")
