
import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🧠 Meme Coin Radar v5.7.2", layout="wide")
st.title("🧠 Meme Coin Radar v5.7.2")
st.markdown("✅ Caches last known data — never shows 'No data' again.")

# Sidebar settings
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh (mins)", 5, 60, 30)
view_mode = st.sidebar.selectbox("🔀 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
rank_mode = st.sidebar.radio("📊 Crypto View", ["Top % Gainers", "Top Volume"])
manual_refresh = st.sidebar.button("🔄 Manual Refresh")

# Meme coin config
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

@st.cache_data(ttl=3600, show_spinner=False)
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
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_top_cryptos_cached():
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
        return coins if isinstance(coins, list) else []
    except:
        return []

def format_price(p):
    if p is None:
        return "N/A"
    elif p >= 0.01:
        return f"${p:,.4f}"
    elif p >= 0.0001:
        return f"${p:,.6f}"
    else:
        return f"${p:.10f}".rstrip("0")

# State for storing last known good data
if "meme_data" not in st.session_state:
    st.session_state.meme_data = {}

if "crypto_data" not in st.session_state:
    st.session_state.crypto_data = []

# Refresh logic
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

if should_refresh:
    st.session_state.last_refresh = now

    if view_mode == "🐸 Meme Coins":
        new_data = {}
        for coin in MEME_COINS:
            data = get_simple_price(coin['gecko'])
            if data:
                new_data[coin['name']] = data
        if new_data:
            st.session_state.meme_data = new_data

    elif view_mode == "💰 Hot Cryptos":
        result = get_top_cryptos_cached()
        if result:
            st.session_state.crypto_data = result

st.markdown(f"⏱️ **Last Refreshed:** {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")

# Render UI
if view_mode == "🐸 Meme Coins":
    st.subheader("🐸 Meme Coin Prices")
    for coin in MEME_COINS:
        data = st.session_state.meme_data.get(coin['name'])
        if data:
            price = data.get("priceUsd")
            change = data.get("priceChange", 0)
            source = data.get("source", "Unknown")
            with st.expander(f"{coin['name']} — {format_price(price)} ({change:.2f}%)", expanded=True):
                st.write(f"**Price:** {format_price(price)}")
                st.write(f"**24h Change:** {change:.2f}%")
                st.write(f"**Source:** {source}")
        else:
            st.warning(f"{coin['name']}: No cached data available.")

elif view_mode == "💰 Hot Cryptos":
    st.subheader("🔥 Hot Cryptos")
    coins = st.session_state.crypto_data
    if coins:
        filtered = []
        if rank_mode == "Top % Gainers":
            filtered = sorted([c for c in coins if c.get("price_change_percentage_24h")],
                              key=lambda x: x["price_change_percentage_24h"], reverse=True)[:15]
        else:
            filtered = sorted([c for c in coins if c.get("total_volume")],
                              key=lambda x: x["total_volume"], reverse=True)[:15]
        for coin in filtered:
            with st.expander(f"{coin['name']} — {coin['price_change_percentage_24h']:.2f}%", expanded=True):
                st.write(f"**Price:** {format_price(coin['current_price'])}")
                st.write(f"**24h Volume:** ${coin['total_volume']:,.0f}")
    else:
        st.info("Using cached crypto data or none available.")
