
import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🧠 Meme Coin Radar v5.7.1", layout="wide")
st.title("🧠 Meme Coin Radar v5.7.1")
st.markdown("🛠 Fallback build with extra safety, live error logging, and no blank screen risk.")

# Sidebar settings
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh (mins)", 5, 60, 30)
view_mode = st.sidebar.selectbox("🔀 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
rank_mode = st.sidebar.radio("📊 Crypto View", ["Top % Gainers", "Top Volume"])
manual_refresh = st.sidebar.button("🔄 Manual Refresh")

# Static meme coin config (Gecko + fallback pair)
MEME_COINS = [
    {"name": "PEPE", "gecko": "pepe"},
    {"name": "SHIB", "gecko": "shiba-inu"},
    {"name": "DOGE", "gecko": "dogecoin"},
    {"name": "FLOKI", "gecko": "floki"},
    {"name": "BONK", "gecko": "bonk"},
    {"name": "WIF", "gecko": "dogwifcoin"},
    {"name": "LADYS", "gecko": "milady-meme-coin"},
    {"name": "TURBO", "gecko": "turbo"},
]

def format_price(p):
    if p is None:
        return "N/A"
    elif p >= 0.01:
        return f"${p:,.4f}"
    elif p >= 0.0001:
        return f"${p:,.6f}"
    else:
        return f"${p:.10f}".rstrip("0")

def get_simple_price(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"}
        r = requests.get(url, params=params)
        if r.status_code != 200:
            return None
        d = r.json().get(coin_id)
        return {
            "priceUsd": d.get("usd"),
            "priceChange": d.get("usd_24h_change"),
            "source": "CoinGecko"
        }
    except Exception as e:
        return {"error": str(e)}

def get_top_cryptos(limit=15, sort_by="gainers"):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        response = requests.get(url, params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 500,
            "page": 1,
            "sparkline": "false"
        })
        coins = response.json()
        if sort_by == "gainers":
            coins = [c for c in coins if c.get('price_change_percentage_24h') is not None]
            return sorted(coins, key=lambda x: x['price_change_percentage_24h'], reverse=True)[:limit]
        else:
            return sorted(coins, key=lambda x: x['total_volume'], reverse=True)[:limit]
    except Exception as e:
        st.error(f"Error loading crypto data: {e}")
        return []

# Refresh logic
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

if should_refresh:
    st.session_state.last_refresh = now
    st.markdown(f"⏱️ **Last Refreshed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if view_mode == "🐸 Meme Coins":
        st.subheader("🐸 Meme Coin Prices")
        for coin in MEME_COINS:
            result = get_simple_price(coin['gecko'])
            if not result:
                st.warning(f"{coin['name']}: No data")
                continue
            if 'error' in result:
                st.error(f"{coin['name']} error: {result['error']}")
                continue

            price = result.get("priceUsd")
            change = result.get("priceChange", 0)
            source = result.get("source", "Unknown")

            with st.expander(f"{coin['name']} — {format_price(price)} ({change:.2f}%)", expanded=True):
                st.write(f"**Price:** {format_price(price)}")
                st.write(f"**24h Change:** {change:.2f}%")
                st.write(f"**Source:** {source}")

    elif view_mode == "💰 Hot Cryptos":
        st.subheader("🔥 Hot Cryptos")
        cryptos = get_top_cryptos(sort_by="volume" if rank_mode == "Top Volume" else "gainers")
        if cryptos:
            for coin in cryptos:
                with st.expander(f"{coin['name']} — {coin['price_change_percentage_24h']:.2f}%", expanded=True):
                    st.write(f"**Price:** {format_price(coin['current_price'])}")
                    st.write(f"**24h Volume:** ${coin['total_volume']:,.0f}")
        else:
            st.warning("⚠️ No crypto data returned.")
