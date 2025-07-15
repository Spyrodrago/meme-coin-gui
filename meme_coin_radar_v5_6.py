
import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import altair as alt

st.set_page_config(page_title="🧠 Meme Coin Radar v5.6", layout="wide")
st.title("🧠 Meme Coin Radar v5.6")
st.markdown("🐸 Meme coin data now uses CoinGecko first, DexScreener as fallback.")

# Sidebar - settings
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh Rate (mins)", 5, 60, 30)
view_mode = st.sidebar.selectbox("🔀 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
rank_mode = st.sidebar.radio("📊 Crypto View Mode", ["Top % Gainers", "Top Volume"], index=0)
manual_refresh = st.sidebar.button("🔄 Refresh Now")

# Meme coin info: name, CoinGecko ID (if available), DexScreener pair (if needed)
MEME_COINS = [
    {"name": "PEPE", "coingecko": "pepe", "dexscreener": "ethereum/0xa43fe16908251ee70ef74718545e4fe6c5ccec9f"},
    {"name": "SHIB", "coingecko": "shiba-inu", "dexscreener": "ethereum/0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce"},
    {"name": "DOGE", "coingecko": "dogecoin", "dexscreener": "bsc/0x233b8b8a2ee367c6ed73b3aa5d84f9d678975f41"},
    {"name": "FLOKI", "coingecko": "floki", "dexscreener": "bsc/0xfb5b838b6cfeedc2873ab27866079ac55363d37e"},
    {"name": "BONK", "coingecko": "bonk", "dexscreener": "solana/DezXzFJgmXarh9FzfbxDPD1C7vKZ5bjrJVd9ESGZc4FQ"},
    {"name": "WIF", "coingecko": "dogwifcoin", "dexscreener": "solana/6Z6gYz65ALzUK4tGkEq1NWBGTTycE9tf6Z9qs1DFKrgv"},
    {"name": "LADYS", "coingecko": "milady-meme-coin", "dexscreener": "ethereum/0x12970e6868f88f6557b76120662c1b3e50a646bf"},
    {"name": "TURBO", "coingecko": "turbo", "dexscreener": "ethereum/0xa5f2211b9b8170f694421f2046281775e8468043"},
    {"name": "COQ", "coingecko": None, "dexscreener": "avalanche/0xb3b1f1e5a776a4a7e0068b9f6ef80d6d4feee528"},
    {"name": "HOPPY", "coingecko": None, "dexscreener": "ethereum/0xcb2cc7ecc09d3f2fc525f4b8c073d043d5b59e5f"}
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

def get_coin_gecko_price(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        data = r.json()
        return {
            "priceUsd": data['market_data']['current_price']['usd'],
            "priceChange": data['market_data']['price_change_percentage_24h'],
            "volume24h": data['market_data']['total_volume']['usd'],
            "source": "CoinGecko"
        }
    except:
        return None

def get_dexscreener_price(pair):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{pair}"
        r = requests.get(url)
        if r.status_code != 200:
            return None
        d = r.json().get("pair")
        if d is None:
            return None
        price = d.get("priceUsd") or d.get("priceNative")
        return {
            "priceUsd": float(price) if price else None,
            "priceChange": float(d.get("priceChange", 0)),
            "volume24h": float(d.get("volume", 0)),
            "source": "DexScreener"
        }
    except:
        return None

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

# Refresh Logic
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

if should_refresh:
    st.session_state.last_refresh = now
    st.markdown(f"⏱️ **Last Refreshed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if view_mode == "🐸 Meme Coins":
        st.subheader("🐸 Meme Coins (Gecko + DexScreener Fallback)")

        for coin in MEME_COINS:
            name = coin['name']
            result = None
            source = ""
            if coin['coingecko']:
                result = get_coin_gecko_price(coin['coingecko'])
            if not result and coin['dexscreener']:
                result = get_dexscreener_price(coin['dexscreener'])
            if result:
                price = result["priceUsd"]
                change = result["priceChange"]
                volume = result["volume24h"]
                source = result["source"]
            else:
                price = change = volume = None
                source = "❌ Unavailable"

            with st.expander(f"{name} — {format_price(price)} ({change if change else 0:.2f}%)", expanded=True):
                st.write(f"**Price:** {format_price(price)}")
                st.write(f"**24h Change:** {change if change else 0:.2f}%")
                st.write(f"**Volume:** ${volume:,.0f}" if volume else "N/A")
                st.write(f"**Source:** {source}")

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
