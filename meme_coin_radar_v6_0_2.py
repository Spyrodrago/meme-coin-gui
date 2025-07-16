
import streamlit as st
import requests
import time
from datetime import datetime
import math

st.set_page_config(page_title="🧠 Meme Coin Radar v6.0.2", layout="wide")
st.title("🧠 Meme Coin Radar v6.0.2")
st.markdown("✅ Sidebar menus restored | 🚀 Crypto display fixed | 🧠 AI scoring active")

TABS = st.tabs(["🐸 Meme Coins", "💰 Hot Cryptos"])

refresh_interval = st.sidebar.slider("⏱️ Auto Refresh (mins)", 5, 60, 30)
manual_refresh = st.sidebar.button("🔄 Manual Refresh")

# Coin lists
MEME_COINS = {
    "PEPE": "pepe-pepe",
    "SHIB": "shiba-inu-shib",
    "DOGE": "dogecoin-doge",
    "FLOKI": "floki-inu-floki",
    "BONK": "bonk-bonk",
    "WIF": "dogwifcoin-wif",
    "LADYS": "milady-meme-ladys",
    "TURBO": "turbo-turbo"
}

CRYPTO_COINS = {
    "BTC": "bitcoin-btc",
    "ETH": "ethereum-eth",
    "SOL": "solana-sol",
    "XRP": "ripple-xrp",
    "ADA": "cardano-ada",
    "LINK": "chainlink-link",
    "TON": "toncoin-ton",
    "ORDI": "ordi-ordi",
    "PIXEL": "pixels-pixel"
}

DEFAULT_MEMES = ["PEPE", "SHIB", "DOGE", "FLOKI", "BONK"]
DEFAULT_CRYPTOS = ["BTC", "ETH", "SOL", "XRP", "ADA"]

if "coin_data" not in st.session_state:
    st.session_state.coin_data = {}
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

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
            "marketCap": d["quotes"]["USD"].get("market_cap", 0),
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

def ai_score(coin):
    score = 0
    try:
        if coin["priceChange"] > 0:
            score += coin["priceChange"] * 2
        if coin["volume24h"] > 0:
            score += math.log10(coin["volume24h"])
    except:
        pass
    return round(score, 2)

# Meme Coins Tab
with TABS[0]:
    st.subheader("🐸 Meme Coins Dashboard")
    meme_selected = st.sidebar.multiselect("✅ Select Meme Coins", options=list(MEME_COINS.keys()), default=DEFAULT_MEMES, key="meme_menu")

    if should_refresh:
        meme_results = {}
        for coin in meme_selected:
            data = fetch_coinpaprika_coin(MEME_COINS[coin])
            if data:
                data["score"] = ai_score(data)
                meme_results[coin] = data
        if meme_results:
            st.session_state.coin_data["memes"] = meme_results
            st.session_state.last_refresh = now

    meme_data = st.session_state.coin_data.get("memes", {})
    for coin in meme_selected:
        data = meme_data.get(coin)
        if data:
            with st.expander(f"{coin} — {format_price(data['priceUsd'])} | AI Score: {data['score']}", expanded=True):
                st.write(f"**Price:** {format_price(data['priceUsd'])}")
                st.write(f"**24h Change:** {data['priceChange']:.2f}%")
                st.write(f"**Volume:** ${data['volume24h']:,.0f}")
                st.write(f"**AI Score:** {data['score']}")
                st.write(f"**Source:** {data['source']}")

# Crypto Tab
with TABS[1]:
    st.subheader("💰 Hot Crypto Dashboard")
    crypto_selected = st.sidebar.multiselect("✅ Select Cryptos", options=list(CRYPTO_COINS.keys()), default=DEFAULT_CRYPTOS, key="crypto_menu")

    if should_refresh:
        crypto_results = {}
        for coin in crypto_selected:
            data = fetch_coinpaprika_coin(CRYPTO_COINS[coin])
            if data:
                data["score"] = ai_score(data)
                crypto_results[coin] = data
        if crypto_results:
            st.session_state.coin_data["cryptos"] = crypto_results
            st.session_state.last_refresh = now

    crypto_data = st.session_state.coin_data.get("cryptos", {})
    for coin in crypto_selected:
        data = crypto_data.get(coin)
        if data:
            with st.expander(f"{coin} — {format_price(data['priceUsd'])} | AI Score: {data['score']}", expanded=True):
                st.write(f"**Price:** {format_price(data['priceUsd'])}")
                st.write(f"**24h Change:** {data['priceChange']:.2f}%")
                st.write(f"**Volume:** ${data['volume24h']:,.0f}")
                st.write(f"**AI Score:** {data['score']}")
                st.write(f"**Source:** {data['source']}")

st.markdown(f"🕒 **Last Updated:** {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")
