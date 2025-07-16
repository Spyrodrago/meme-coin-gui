
# v6.1.7 full version rebuild
# - Crypto display restored
# - Meme coin dropdown fix
# - Safe scoring and fallback retained
# - Full dashboard functionality

import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🧠 Meme Coin Radar v6.1.7", layout="wide")
st.title("🧠 Meme Coin Radar v6.1.7")

view_mode = st.sidebar.radio("📊 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh (mins)", 5, 60, 30)
manual_refresh = st.sidebar.button("🔄 Manual Refresh")

MEME_COINS = {
    "PEPE": "pepe", "SHIB": "shiba-inu", "DOGE": "dogecoin", "FLOKI": "floki",
    "BONK": "bonk", "WIF": "dogwifhat", "LADYS": "milady-meme-coin", "TURBO": "turbo",
    "PIT": "pitbull", "HOGE": "hoge-finance", "SAMO": "samoyedcoin", "VOLT": "volt-inu",
    "MOG": "mog-coin", "BORK": "bork", "KISHU": "kishu-inu"
}
CRYPTO_COINS = {
    "BTC": "btc-bitcoin", "ETH": "eth-ethereum", "SOL": "sol-solana", "XRP": "xrp-xrp",
    "ADA": "ada-cardano", "LINK": "link-chainlink", "TON": "ton-toncoin", "ORDI": "ordi-ordi",
    "PIXEL": "pixel-pixels", "AVAX": "avax-avalanche", "NEAR": "near-near-protocol",
    "MATIC": "matic-polygon", "APT": "apt-aptos", "OP": "op-optimism", "INJ": "inj-injective"
}
DEFAULT_MEMES = ["PEPE", "SHIB", "DOGE", "FLOKI", "BONK", "WIF"]
DEFAULT_CRYPTOS = ["BTC", "ETH", "SOL", "XRP", "ADA", "LINK"]

if "coin_data" not in st.session_state:
    st.session_state.coin_data = {}
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0
if "selected_memes" not in st.session_state:
    st.session_state.selected_memes = DEFAULT_MEMES.copy()
if "selected_cryptos" not in st.session_state:
    st.session_state.selected_cryptos = DEFAULT_CRYPTOS.copy()

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

def fetch_coingecko_price(id):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd&include_24hr_change=true"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        d = r.json()
        if id not in d:
            return None
        return {
            "name": id.capitalize(),
            "symbol": id.upper(),
            "priceUsd": d[id]["usd"],
            "priceChange": d[id].get("usd_24h_change", 0),
            "volume24h": 0,
            "marketCap": 0,
            "source": "CoinGecko"
        }
    except:
        return None

def fetch_dexscreener_price(symbol):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={symbol.lower()}"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        data = r.json()
        matches = [p for p in data.get("pairs", []) if p.get("baseToken", {}).get("symbol", "").upper() == symbol.upper()]
        if not matches:
            return None
        pair = matches[0]
        return {
            "name": pair.get("baseToken", {}).get("name", symbol),
            "symbol": pair.get("baseToken", {}).get("symbol", symbol),
            "priceUsd": float(pair.get("priceUsd", 0)),
            "priceChange": float(pair.get("priceChange", 0)),
            "volume24h": float(pair.get("volume", 0)),
            "marketCap": 0,
            "source": "DexScreener"
        }
    except:
        return None

def gpt_score(coin, coin_type="meme"):
    score = 0
    change = coin.get("priceChange") or 0
    volume = coin.get("volume24h") or 0
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

# Coin selection and session updates
if view_mode == "🐸 Meme Coins":
    selected = st.sidebar.multiselect("✅ Select Meme Coins", list(MEME_COINS.keys()), default=DEFAULT_MEMES)
    coin_ids = {k: MEME_COINS[k] for k in selected}
    st.session_state.selected_memes = selected
    coin_type = "meme"
    group_key = "memes"
else:
    selected = st.sidebar.multiselect("✅ Select Cryptos", list(CRYPTO_COINS.keys()), default=DEFAULT_CRYPTOS)
    coin_ids = {k: CRYPTO_COINS[k] for k in selected}
    st.session_state.selected_cryptos = selected
    coin_type = "crypto"
    group_key = "cryptos"

# Fetch
if should_refresh:
    results = {}
    for symbol, id_slug in coin_ids.items():
        data = None
        if coin_type == "crypto":
            data = fetch_coinpaprika_coin(id_slug)
            if not data:
                data = fetch_coingecko_price(id_slug.split("-")[1])
            if not data:
                data = fetch_dexscreener_price(symbol)
        else:
            data = fetch_dexscreener_price(symbol)
            if not data:
                data = fetch_coingecko_price(id_slug)
        if data:
            data["score"] = gpt_score(data, coin_type)
            results[symbol] = data
    if results:
        st.session_state.coin_data[group_key] = results
        st.session_state.last_refresh = now

# Display coins
st.subheader(f"{view_mode} Dashboard")
data = st.session_state.coin_data.get(group_key, {})
for coin in selected:
    coin_data = data.get(coin)
    if coin_data:
        with st.expander(f"{coin} — {format_price(coin_data['priceUsd'])} | AI Score: {coin_data['score']}", expanded=True):
            st.write(f"**Price:** {format_price(coin_data['priceUsd'])}")
            st.write(f"**24h Change:** {coin_data['priceChange']:.2f}%")
            st.write(f"**Volume:** ${coin_data['volume24h']:,.0f}")
            st.write(f"**AI Score:** {coin_data['score']}")
            st.write(f"**Source:** {coin_data['source']}")
st.markdown(f"🕒 **Last Updated:** {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")
