
import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import altair as alt

st.set_page_config(page_title="💰 Meme Coin Radar v4", layout="wide")
st.title("💰 Meme Coin Radar v4")
st.markdown("Real-time tracking for meme coins, hot cryptos, and instant alerts.")

# --- Sidebar ---
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("⏱️ Refresh (mins)", 5, 60, 30)
enable_new_coin_scan = st.sidebar.checkbox("🧪 Scan for new meme coins", value=True)
enable_hot_crypto_scan = st.sidebar.checkbox("🔥 Show hot cryptos (non-meme)", value=True)

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

selected_coins = st.sidebar.multiselect("Track these meme coins", list(COINS_ALL.keys()), default=list(COINS_ALL.keys()))
MEME_KEYWORDS = ["dog", "elon", "shib", "pepe", "cat", "floki", "moon", "inu", "bonk", "wif"]

# --- Alert Functions ---
def send_discord_alert(message, webhook_url=""):
    if webhook_url:
        try:
            requests.post(webhook_url, json={"content": message})
        except:
            pass

def send_telegram_alert(message, bot_token="", chat_id=""):
    if bot_token and chat_id:
        try:
            requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage", params={"chat_id": chat_id, "text": message})
        except:
            pass

# --- Data Functions ---
def get_price_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    data = response.json()
    market = data.get("market_data", {})
    price = market.get("current_price", {}).get("usd", 0)
    change_24h = market.get("price_change_percentage_24h", 0)
    volume = market.get("total_volumes", {}).get("usd", 0)
    sparkline = market.get("sparkline_7d", {}).get("price", [])
    return {
        "price": price,
        "change_24h": change_24h,
        "volume": volume,
        "sparkline": sparkline,
        "rsi": 50  # placeholder
    }

def check_buy_signal(data):
    signals = 0
    if data["change_24h"] <= -10:
        signals += 1
    if data["rsi"] <= 35:
        signals += 1
    if data["volume"] >= 5000000:
        signals += 1
    return signals >= 2

def find_hot_new_coins():
    url = "https://api.coingecko.com/api/v3/coins/list?include_platform=false"
    hot_alerts = []
    try:
        response = requests.get(url)
        coins = response.json()[-50:]
        for coin in coins:
            coin_id = coin['id']
            try:
                data = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}").json()
                name = data['name'].lower()
                price = data['market_data']['current_price']['usd']
                change = data['market_data'].get('price_change_percentage_24h', 0)
                volume = data['market_data']['total_volumes']['usd']
                if any(word in name for word in MEME_KEYWORDS):
                    if change >= 50 and volume > 250000:
                        alert = f"🧪 NEW COIN: '{coin['name']}' +{change:.1f}%, vol ${volume:,.0f}"
                        hot_alerts.append(alert)
                        send_discord_alert(alert)
                        send_telegram_alert(alert)
            except:
                continue
    except:
        return []
    return hot_alerts

def get_top_hot_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    try:
        response = requests.get(url, params={"vs_currency": "usd", "order": "volume_desc", "per_page": 50, "page": 1})
        top = []
        for coin in response.json():
            if coin['price_change_percentage_24h'] and coin['price_change_percentage_24h'] > 10 and coin['market_cap_rank'] <= 100:
                top.append({
                    "name": coin['name'],
                    "price": coin['current_price'],
                    "change": coin['price_change_percentage_24h'],
                    "volume": coin['total_volume']
                })
        return sorted(top, key=lambda x: x['change'], reverse=True)[:5]
    except:
        return []

# --- Main Execution ---
st.markdown(f"🕒 Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
for coin_id in selected_coins:
    try:
        data = get_price_data(coin_id)
        name = COINS_ALL[coin_id]
        st.markdown(f"### {name}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Price:** ${data['price']:.6f}")
            st.write(f"**24h Change:** {data['change_24h']:.2f}%")
            st.write(f"**Volume:** ${data['volume']:,.0f}")
            if check_buy_signal(data):
                st.error(f"🚨 BUY ALERT: {name} meets dip criteria!")
                send_discord_alert(f"🚨 BUY ALERT: {name} triggered.")
                send_telegram_alert(f"🚨 BUY ALERT: {name} triggered.")
        with col2:
            if data["sparkline"]:
                df = pd.DataFrame({
                    "hour": list(range(len(data["sparkline"]))),
                    "price": data["sparkline"]
                })
                chart = alt.Chart(df).mark_line().encode(x="hour", y="price").properties(height=100)
                st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"Error with {coin_id}: {e}")

if enable_new_coin_scan:
    st.subheader("🧪 New Meme Coin Scans")
    new_alerts = find_hot_new_coins()
    if new_alerts:
        for alert in new_alerts:
            st.success(alert)
    else:
        st.info("No hot meme coins found.")

if enable_hot_crypto_scan:
    st.subheader("🔥 Hot Cryptos (Non-Meme)")
    hot_cryptos = get_top_hot_cryptos()
    if hot_cryptos:
        for coin in hot_cryptos:
            st.success(f"{coin['name']} +{coin['change']:.2f}% | ${coin['price']:.4f} | Vol: ${coin['volume']:,.0f}")
    else:
        st.info("No hot non-meme cryptos found.")

# Auto-refresh
time.sleep(refresh_interval * 60)
st.experimental_rerun()
