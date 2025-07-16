
import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🧠 Meme Coin Radar v5.8.1", layout="wide")
st.title("🧠 Meme Coin Radar v5.8.1")
st.markdown("🔒 Fallback-safe version with CoinPaprika. Guaranteed load, even if API fails.")

# Sidebar
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh (mins)", 5, 60, 30)
view_mode = st.sidebar.selectbox("🔀 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
rank_mode = st.sidebar.radio("📊 Crypto View", ["Top % Gainers", "Top Volume"])
manual_refresh = st.sidebar.button("🔄 Manual Refresh")

# Meme Coin Config (CoinPaprika IDs)
MEME_COINS = [
    {"name": "PEPE", "id": "pepe-pepe"},
    {"name": "SHIB", "id": "shiba-inu-shib"},
    {"name": "DOGE", "id": "dogecoin-doge"},
    {"name": "FLOKI", "id": "floki-inu-floki"},
    {"name": "BONK", "id": "bonk-bonk"},
    {"name": "WIF", "id": "dogwifcoin-wif"},
    {"name": "LADYS", "id": "milady-meme-ladys"},
    {"name": "TURBO", "id": "turbo-turbo"},
]

# Fetch single coin (meme)
def fetch_coinpaprika_coin(id):
    try:
        url = f"https://api.coinpaprika.com/v1/tickers/{id}"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        d = r.json()
        return {
            "name": d.get("name"),
            "symbol": d.get("symbol"),
            "priceUsd": d["quotes"]["USD"]["price"],
            "priceChange": d["quotes"]["USD"]["percent_change_24h"],
            "source": "CoinPaprika"
        }
    except Exception as e:
        return {"error": str(e)}

# Fetch all cryptos
def fetch_all_cryptos():
    try:
        url = "https://api.coinpaprika.com/v1/tickers"
        r = requests.get(url)
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        st.error(f"Crypto fetch error: {e}")
        return []

# Price formatting
def format_price(p):
    if p is None:
        return "N/A"
    elif p >= 0.01:
        return f"${p:,.4f}"
    elif p >= 0.0001:
        return f"${p:,.6f}"
    else:
        return f"${p:.10f}".rstrip("0")

# State
if "meme_data" not in st.session_state:
    st.session_state.meme_data = {}
if "crypto_data" not in st.session_state:
    st.session_state.crypto_data = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

# Refresh logic
if should_refresh:
    st.session_state.last_refresh = now

    if view_mode == "🐸 Meme Coins":
        results = {}
        for coin in MEME_COINS:
            data = fetch_coinpaprika_coin(coin["id"])
            if data and "priceUsd" in data:
                results[coin["name"]] = data
        if results:
            st.session_state.meme_data = results

    elif view_mode == "💰 Hot Cryptos":
        all_data = fetch_all_cryptos()
        if all_data:
            st.session_state.crypto_data = all_data

st.markdown(f"⏱️ **Last Refresh:** {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")

# Display Meme Coins
if view_mode == "🐸 Meme Coins":
    st.subheader("🐸 Meme Coins (CoinPaprika)")
    if not st.session_state.meme_data:
        st.warning("No meme coin data available.")
    else:
        for coin in MEME_COINS:
            data = st.session_state.meme_data.get(coin["name"])
            if data:
                price = data["priceUsd"]
                change = data["priceChange"]
                with st.expander(f"{coin['name']} — {format_price(price)} ({change:.2f}%)", expanded=True):
                    st.write(f"**Price:** {format_price(price)}")
                    st.write(f"**24h Change:** {change:.2f}%")
                    st.write(f"**Source:** CoinPaprika")

# Display Hot Cryptos
elif view_mode == "💰 Hot Cryptos":
    st.subheader("🔥 Hot Cryptos (CoinPaprika)")
    if not st.session_state.crypto_data:
        st.warning("No crypto data available.")
    else:
        coins = st.session_state.crypto_data
        if rank_mode == "Top % Gainers":
            sorted_data = sorted(coins, key=lambda x: x["quotes"]["USD"].get("percent_change_24h", 0), reverse=True)[:15]
        else:
            sorted_data = sorted(coins, key=lambda x: x["quotes"]["USD"].get("volume_24h", 0), reverse=True)[:15]

        for coin in sorted_data:
            name = coin["name"]
            price = coin["quotes"]["USD"]["price"]
            change = coin["quotes"]["USD"].get("percent_change_24h", 0)
            volume = coin["quotes"]["USD"].get("volume_24h", 0)
            with st.expander(f"{name} — {change:.2f}%", expanded=True):
                st.write(f"**Price:** {format_price(price)}")
                st.write(f"**24h Volume:** ${volume:,.0f}")
