
import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🧠 Meme Coin Radar v6.0 (Alpha)", layout="wide")
st.title("🧠 Meme Coin Radar v6.0")
st.markdown("🚀 Custom coin tracking, AI radar placeholder, and alert prep.")

# Sidebar controls
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh (mins)", 5, 60, 30)
manual_refresh = st.sidebar.button("🔄 Manual Refresh")

# Full list of selectable coins (meme + top crypto)
ALL_COINS = {
    "PEPE": "pepe-pepe",
    "SHIB": "shiba-inu-shib",
    "DOGE": "dogecoin-doge",
    "FLOKI": "floki-inu-floki",
    "BONK": "bonk-bonk",
    "WIF": "dogwifcoin-wif",
    "LADYS": "milady-meme-ladys",
    "TURBO": "turbo-turbo",
    "BTC": "bitcoin-btc",
    "ETH": "ethereum-eth",
    "SOL": "solana-sol",
    "XRP": "ripple-xrp",
    "ADA": "cardano-ada",
    "LINK": "chainlink-link"
}

default_selection = ["PEPE", "SHIB", "DOGE", "BONK", "BTC", "ETH", "SOL"]
selected = st.sidebar.multiselect("🪙 Select coins to track", list(ALL_COINS.keys()), default=default_selection)

# Function to fetch data from CoinPaprika
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
            "volume24h": d["quotes"]["USD"]["volume_24h"],
            "source": "CoinPaprika"
        }
    except:
        return None

def format_price(p):
    if p is None:
        return "N/A"
    elif p >= 0.01:
        return f"${p:,.4f}"
    elif p >= 0.0001:
        return f"${p:,.6f}"
    else:
        return f"${p:.10f}".rstrip("0")

# Refresh logic
if "coin_data" not in st.session_state:
    st.session_state.coin_data = {}
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

if should_refresh:
    st.session_state.last_refresh = now
    results = {}
    for coin in selected:
        data = fetch_coinpaprika_coin(ALL_COINS[coin])
        if data:
            results[coin] = data
    if results:
        st.session_state.coin_data = results

st.markdown(f"⏱️ **Last Refresh:** {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")

# Display selected coins
st.subheader("📊 Tracked Coin Dashboard")
for coin in selected:
    data = st.session_state.coin_data.get(coin)
    if data:
        with st.expander(f"{coin} — {format_price(data['priceUsd'])} ({data['priceChange']:.2f}%)", expanded=True):
            st.write(f"**Price:** {format_price(data['priceUsd'])}")
            st.write(f"**24h Change:** {data['priceChange']:.2f}%")
            st.write(f"**24h Volume:** ${data['volume24h']:,.0f}")
            st.write(f"**Source:** {data['source']}")

# Placeholder AI model section
st.subheader("🧠 AI Radar (Coming Soon)")
st.info("This panel will show coins ranked by smart predictive scores in the next update.")

# Placeholder alert toggle
st.subheader("🚨 Alert System (Coming Soon)")
st.info("You'll soon be able to get alerts for price spikes via Telegram or Discord.")
