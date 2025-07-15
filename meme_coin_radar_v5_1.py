
import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import altair as alt

st.set_page_config(page_title="🧠 Meme Coin Radar v5.1", layout="wide")
st.title("🧠 Meme Coin Radar v5.1")
st.markdown("Live radar for meme coins, trending cryptos, real prices, and alerts.")

# Sidebar - settings
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Auto Refresh Rate (mins)", 5, 60, 30)
view_mode = st.sidebar.selectbox("🔀 View Mode", ["🐸 Meme Coins", "💰 Hot Cryptos"])
manual_refresh = st.sidebar.button("🔄 Refresh Now")

COINS_ALL = {
    "pepe": "PEPE",
    "dogecoin": "DOGE",
    "shiba-inu": "SHIB",
    "floki": "FLOKI",
    "dogwifhat": "WIF",
    "bonk": "BONK",
    "turbo": "TURBO",
    "milady-meme-coin": "LADYS",
    "hoppy": "HOPPY",
    "coq-inu": "COQ"
}

selected_coins = list(COINS_ALL.keys())
MEME_KEYWORDS = ["dog", "elon", "shib", "pepe", "cat", "floki", "moon", "inu", "bonk", "wif"]

# Utility Functions
def format_price(p):
    if p is None:
        return "N/A"
    elif p >= 0.01:
        return f"${p:,.4f}"
    elif p >= 0.0001:
        return f"${p:,.6f}"
    else:
        return f"${p:.10f}".rstrip("0")

def get_price_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        response = requests.get(url)
        data = response.json()
        market = data.get("market_data", {})
        price = market.get("current_price", {}).get("usd", None)
        change_24h = market.get("price_change_percentage_24h", 0)
        volume = market.get("total_volumes", {}).get("usd", 0)
        sparkline = market.get("sparkline_7d", {}).get("price", [])
        return {
            "price": price,
            "change_24h": change_24h,
            "volume": volume,
            "sparkline": sparkline,
            "rsi": 50
        }
    except:
        return {"price": None, "change_24h": 0, "volume": 0, "sparkline": [], "rsi": 50}

def check_buy_signal(data):
    return (
        (data["change_24h"] <= -10) +
        (data["rsi"] <= 35) +
        (data["volume"] >= 5000000)
    ) >= 2

def get_top_hot_cryptos(limit=10):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    try:
        response = requests.get(url, params={"vs_currency": "usd", "order": "percent_change_24h_desc", "per_page": 250, "page": 1})
        top = []
        for coin in response.json():
            if coin['price_change_percentage_24h'] and coin['price_change_percentage_24h'] > 5:
                top.append({
                    "name": coin['name'],
                    "price": coin['current_price'],
                    "change": coin['price_change_percentage_24h'],
                    "volume": coin['total_volume']
                })
        return sorted(top, key=lambda x: x['change'], reverse=True)[:limit]
    except:
        return []

# Manual and auto refresh logic
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

now = time.time()
should_refresh = manual_refresh or (now - st.session_state.last_refresh > refresh_interval * 60)

if should_refresh:
    st.session_state.last_refresh = now

    st.markdown(f"⏱️ **Last Refreshed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if view_mode == "🐸 Meme Coins":
        st.subheader("📊 Meme Coin Market")

        for coin_id in selected_coins:
            data = get_price_data(coin_id)
            name = COINS_ALL[coin_id]
            price_display = format_price(data["price"])
            with st.expander(f"{name} ({price_display}) — {data['change_24h']:.2f}%", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Price:** {price_display}")
                    st.write(f"**24h Change:** {data['change_24h']:.2f}%")
                    st.write(f"**Volume:** ${data['volume']:,.0f}")
                    if check_buy_signal(data):
                        st.error(f"🚨 BUY ALERT for {name}!")
                with col2:
                    if data["sparkline"]:
                        df = pd.DataFrame({
                            "hour": list(range(len(data["sparkline"]))),
                            "price": data["sparkline"]
                        })
                        chart = alt.Chart(df).mark_line().encode(x="hour", y="price").properties(height=100)
                        st.altair_chart(chart, use_container_width=True)

    elif view_mode == "💰 Hot Cryptos":
        st.subheader("🔥 Top Trending Cryptos")
        hot_cryptos = get_top_hot_cryptos()
        if hot_cryptos:
            for coin in hot_cryptos:
                price_display = format_price(coin['price'])
                with st.expander(f"{coin['name']} — +{coin['change']:.2f}%", expanded=True):
                    st.write(f"**Price:** {price_display}")
                    st.write(f"**24h Volume:** ${coin['volume']:,.0f}")
        else:
            st.info("No hot cryptos found at this time.")
