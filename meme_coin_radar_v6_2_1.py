
# Meme Coin Radar v6.2.1
# Fixes: LunarCrush data, AI score labels, scoring explanation

import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🚀 Meme Coin Radar v6.2.1", layout="wide")
st.title("🚀 Meme Coin Radar v6.2.1")

view_mode = st.sidebar.radio("📊 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh (mins)", 5, 60, 30)
manual_refresh = st.sidebar.button("🔄 Manual Refresh")

LUNARCRUSH_API_KEY = "y941kj0vv35jv4xzmbksryrumd6qnrv0gge7v67"

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

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

def fetch_lunarcrush_metrics(symbol):
    try:
        url = f"https://api.lunarcrush.com/v2?data=assets&key={LUNARCRUSH_API_KEY}&symbol={symbol.upper()}"
        r = requests.get(url)
        if r.status_code != 200:
            return {}
        data = r.json()
        item = data["data"][0] if "data" in data and data["data"] else {}
        return {
            "social_volume": item.get("social_volume"),
            "social_score": item.get("galaxy_score"),
            "sentiment": item.get("average_sentiment"),
            "alt_rank": item.get("alt_rank")
        }
    except:
        return {}

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

def gpt_score(coin, coin_type="meme", social=None):
    score = 0
    change = coin.get("priceChange") or 0
    volume = coin.get("volume24h") or 0
    if change > 20: score += 10
    elif change > 10: score += 8
    elif change > 5: score += 6
    elif change > 0: score += 4
    elif change > -5: score += 2
    if volume > 1_000_000_000: score += 5
    elif volume > 500_000_000: score += 4
    elif volume > 100_000_000: score += 3
    elif volume > 10_000_000: score += 2
    if social:
        if social.get("social_score", 0) > 60: score += 3
        if social.get("social_volume", 0) > 10000: score += 2
        if social.get("alt_rank", 100) < 30: score += 2
    if coin_type == "meme" and score > 9:
        score += 1
    return round(score, 1)

def interpret_score(score):
    if score >= 13: return "✅ Strong Buy"
    elif score >= 10: return "Buy"
    elif score >= 7: return "Possible Buy"
    elif score >= 4: return "Hold"
    elif score >= 2: return "Possible Sell"
    else: return "🚫 Sell"

def format_price(p):
    if p is None:
        return "N/A"
    elif p >= 0.01:
        return f"${p:,.4f}"
    elif p >= 0.0001:
        return f"${p:,.6f}"
    else:
        return f"${p:.10f}".rstrip("0")

# Selections
if view_mode == "🐸 Meme Coins":
    selected_memes = st.sidebar.multiselect("✅ Select Meme Coins", list(MEME_COINS.keys()), default=DEFAULT_MEMES)
    coin_ids = {k: MEME_COINS[k] for k in selected_memes}
    coin_type = "meme"
    group_key = "memes"
else:
    selected_cryptos = st.sidebar.multiselect("✅ Select Cryptos", list(CRYPTO_COINS.keys()), default=DEFAULT_CRYPTOS)
    coin_ids = {k: CRYPTO_COINS[k] for k in selected_cryptos}
    coin_type = "crypto"
    group_key = "cryptos"

# Fetch logic
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
        social = fetch_lunarcrush_metrics(symbol)
        if data:
            data["social"] = social
            data["score"] = gpt_score(data, coin_type, social)
            results[symbol] = data
    if results:
        st.session_state.coin_data[group_key] = results
        st.session_state.last_refresh = now

# Display
st.subheader(f"{view_mode} Dashboard")
data = st.session_state.coin_data.get(group_key, {})
display_coins = list(coin_ids.keys())

for coin in display_coins:
    coin_data = data.get(coin)
    if coin_data:
        with st.expander(f"{coin} — {format_price(coin_data['priceUsd'])} | AI: {interpret_score(coin_data['score'])} ({coin_data['score']})", expanded=True):
            st.write(f"**Price:** {format_price(coin_data['priceUsd'])}")
            st.write(f"**24h Change:** {coin_data['priceChange']:.2f}%")
            st.write(f"**Volume:** ${coin_data['volume24h']:,.0f}")
            st.write(f"**AI Score:** {coin_data['score']} → _{interpret_score(coin_data['score'])}_")
            st.write(f"**Social Volume:** {coin_data.get('social', {}).get('social_volume', 'N/A')}")
            st.write(f"**Social Score:** {coin_data.get('social', {}).get('social_score', 'N/A')}")
            st.write(f"**Alt Rank:** {coin_data.get('social', {}).get('alt_rank', 'N/A')}")
            st.write(f"**Source:** {coin_data['source']}")

st.markdown(f"🕒 **Last Updated:** {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")

with st.expander("ℹ️ What does the AI Score mean?", expanded=False):
    st.markdown("""
- **✅ Strong Buy** (13+): Major price, volume, and social momentum.
- **Buy** (10–12): High potential to rise further.
- **Possible Buy** (7–9): Trending positively, early movement.
- **Hold** (4–6): Stable or unclear signals.
- **Possible Sell** (2–3): Weak activity or early dip.
- **🚫 Sell** (0–1): Negative signals or downtrend.
""")
