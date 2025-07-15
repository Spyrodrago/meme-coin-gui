
import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import altair as alt

st.set_page_config(page_title="🧠 Meme Coin Radar v5.5", layout="wide")
st.title("🧠 Meme Coin Radar v5.5")
st.markdown("🔧 Meme coin prices now use verified, active DexScreener pairs.")

# Sidebar - settings
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh Rate (mins)", 5, 60, 30)
view_mode = st.sidebar.selectbox("🔀 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
rank_mode = st.sidebar.radio("📊 Crypto View Mode", ["Top % Gainers", "Top Volume"], index=0)
manual_refresh = st.sidebar.button("🔄 Refresh Now")

# Verified working DexScreener pair IDs
DEXSCREENER_PAIRS = {
    "PEPE": "ethereum/0xa43fe16908251ee70ef74718545e4fe6c5ccec9f",  # UniSwap V2
    "DOGE": "bsc/0x233b8b8a2ee367c6ed73b3aa5d84f9d678975f41",       # PancakeSwap V2
    "SHIB": "ethereum/0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",  # UniSwap V2
    "FLOKI": "bsc/0xfb5b838b6cfeedc2873ab27866079ac55363d37e",      # PancakeSwap V2
    "WIF": "solana/6Z6gYz65ALzUK4tGkEq1NWBGTTycE9tf6Z9qs1DFKrgv",   # Solana
    "BONK": "solana/DezXzFJgmXarh9FzfbxDPD1C7vKZ5bjrJVd9ESGZc4FQ",  # Solana
    "TURBO": "ethereum/0xa5f2211b9b8170f694421f2046281775e8468043", # UniSwap V2
    "LADYS": "ethereum/0x12970e6868f88f6557b76120662c1b3e50a646bf", # UniSwap V2
    "HOPPY": "ethereum/0xcb2cc7ecc09d3f2fc525f4b8c073d043d5b59e5f", # UniSwap V2
    "COQ": "avalanche/0xb3b1f1e5a776a4a7e0068b9f6ef80d6d4feee528"   # TraderJoe
}

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
        if r.status_code != 200:
            return {"symbol": "???", "priceUsd": None, "priceChange": 0, "volume24h": 0, "sparkline": [], "status": f"❌ HTTP {r.status_code}"}
        d = r.json().get("pair")
        if d is None:
            return {"symbol": "???", "priceUsd": None, "priceChange": 0, "volume24h": 0, "sparkline": [], "status": "⚠️ No data found"}
        price = d.get("priceUsd") or d.get("priceNative")
        return {
            "symbol": d.get("baseToken", {}).get("symbol", "???"),
            "priceUsd": float(price) if price else None,
            "priceChange": float(d.get("priceChange", 0)),
            "volume24h": float(d.get("volume", 0)),
            "sparkline": d.get("priceChart", []),
            "status": "✅ OK" if price else "⚠️ No price available"
        }
    except Exception as e:
        return {
            "symbol": "???",
            "priceUsd": None,
            "priceChange": 0,
            "volume24h": 0,
            "sparkline": [],
            "status": f"❌ Error: {str(e)}"
        }

def get_top_cryptos(limit=15, sort_by="gainers"):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    try:
        response = requests.get(url, params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 500, "page": 1})
        coins = response.json()
        if sort_by == "gainers":
            coins = [c for c in coins if c.get('price_change_percentage_24h') is not None]
            return sorted(coins, key=lambda x: x['price_change_percentage_24h'], reverse=True)[:limit]
        else:
            return sorted(coins, key=lambda x: x['total_volume'], reverse=True)[:limit]
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
        st.subheader("📊 Meme Coins (Verified DexScreener Pairs)")
        for name, pair in DEXSCREENER_PAIRS.items():
            data = get_dexscreener_data(pair)
            with st.expander(f"{name} — {format_price(data['priceUsd'])} ({data['priceChange']}%)", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Price:** {format_price(data['priceUsd'])}")
                    st.write(f"**24h Change:** {data['priceChange']}%")
                    st.write(f"**Volume:** ${data['volume24h']:,.0f}")
                    st.write(f"**Status:** {data['status']}")
                with col2:
                    if data["sparkline"]:
                        df = pd.DataFrame({
                            "point": list(range(len(data["sparkline"]))),
                            "price": [float(p) for p in data["sparkline"]]
                        })
                        chart = alt.Chart(df).mark_line().encode(x="point", y="price").properties(height=100)
                        st.altair_chart(chart, use_container_width=True)

    elif view_mode == "💰 Hot Cryptos":
        st.subheader("🔥 Top Trending Cryptos")
        hot_cryptos = get_top_cryptos(sort_by="volume" if rank_mode == "Top Volume" else "gainers")
        if hot_cryptos:
            for coin in hot_cryptos:
                with st.expander(f"{coin['name']} — {coin['price_change_percentage_24h']:.2f}%", expanded=True):
                    st.write(f"**Price:** {format_price(coin['current_price'])}")
                    st.write(f"**24h Volume:** ${coin['total_volume']:,.0f}")
        else:
            st.info("No trending cryptos found.")
