
import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🧠 Meme Coin Radar v6.1", layout="wide")
st.title("🧠 Meme Coin Radar v6.1")
st.markdown("🔍 Now powered by GPT-style scoring • Checkbox selection • Crypto fix • Cleaner interface")

# Sidebar view toggle
view_mode = st.sidebar.radio("📊 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh (mins)", 5, 60, 30)
manual_refresh = st.sidebar.button("🔄 Manual Refresh")

# Coin definitions
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

# Session storage
if "coin_data" not in st.session_state:
    st.session_state.coin_data = {}
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

# Coin fetcher
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

# GPT-style scoring logic
def gpt_score(coin, coin_type="meme"):
    score = 0
    change = coin.get("priceChange", 0)
    volume = coin.get("volume24h", 0)

    if change > 20: score += 9
    elif change > 10: score += 7
    elif change > 5: score += 5
    elif change > 0: score += 3
    elif change > -5: score += 1

    if volume > 1_000_000_000: score += 5
    elif volume > 500_000_000: score += 4
    elif volume > 100_000_000: score += 3
    elif volume > 10_000_000: score += 2

    if coin_type == "meme" and score > 8:
        score += 1

    return round(score, 1)

def format_price(p):
    if p is None:
        return "N/A"
    elif p >= 0.01:
        return f"${p:,.4f}"
    elif p >= 0.0001:
        return f"${p:,.6f}"
    else:
        return f"${p:.10f}".rstrip("0")

# Select coin set
coin_map = MEME_COINS if view_mode == "🐸 Meme Coins" else CRYPTO_COINS
default_list = DEFAULT_MEMES if view_mode == "🐸 Meme Coins" else DEFAULT_CRYPTOS
coin_type = "meme" if view_mode == "🐸 Meme Coins" else "crypto"
coin_group = []

# Dashboard checkbox selection
st.subheader(f"{view_mode} Dashboard")
st.markdown("✅ **Select which coins to display:**")
cols = st.columns(3)
for i, coin in enumerate(coin_map):
    default = coin in default_list
    with cols[i % 3]:
        if st.checkbox(coin, value=default, key=f"{coin_type}_{coin}"):
            coin_group.append(coin)

# Refresh + data fetch
if should_refresh:
    results = {}
    for coin in coin_group:
        data = fetch_coinpaprika_coin(coin_map[coin])
        if data:
            data["score"] = gpt_score(data, coin_type)
            results[coin] = data
    if results:
        st.session_state.coin_data[view_mode] = results
        st.session_state.last_refresh = now

# Display coins
data = st.session_state.coin_data.get(view_mode, {})
for coin in coin_group:
    coin_data = data.get(coin)
    if coin_data:
        with st.expander(f"{coin} — {format_price(coin_data['priceUsd'])} | AI Score: {coin_data['score']}", expanded=True):
            st.write(f"**Price:** {format_price(coin_data['priceUsd'])}")
            st.write(f"**24h Change:** {coin_data['priceChange']:.2f}%")
            st.write(f"**Volume:** ${coin_data['volume24h']:,.0f}")
            st.write(f"**AI Score:** {coin_data['score']}")
            st.write(f"**Source:** {coin_data['source']}")

# Footer
st.markdown(f"🕒 **Last Updated:** {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")
