
# Meme Coin Radar v6.2.3 — Fix LunarCrush with debug logging & strict fallback

import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="🚀 Meme Coin Radar v6.2.3", layout="wide")
st.title("🚀 Meme Coin Radar v6.2.3")

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
        st.write(f"🔍 LunarCrush URL: {url}")
        st.write(f"📥 Status Code: {r.status_code}")
        if r.status_code != 200:
            return {}
        data = r.json()
        st.write(f"📦 Raw LunarCrush Response for {symbol}:")
        st.json(data)

        if not data.get("data") or not isinstance(data["data"], list):
            return {}
        item = data["data"][0]
        return {
            "social_volume": item.get("social_volume") or "N/A",
            "social_score": item.get("galaxy_score") or "N/A",
            "sentiment": item.get("average_sentiment") or "N/A",
            "alt_rank": item.get("alt_rank") or "N/A"
        }
    except Exception as e:
        st.error(f"Error fetching LunarCrush data for {symbol}: {e}")
        return {}

# Placeholder for rest of the app logic...
