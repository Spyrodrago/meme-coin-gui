
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="🧠 Meme Coin Super Bot", layout="wide")
st.title("🚨 Meme Coin Buy Alert + New Hot Coin Detector")

COINS = {
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

MEME_KEYWORDS = ["dog", "elon", "shib", "pepe", "cat", "floki", "moon", "inu", "bonk", "wif"]

def get_price_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    data = response.json()
    market = data.get("market_data", {})
    price = market.get("current_price", {}).get("usd", 0)
    change_24h = market.get("price_change_percentage_24h", 0)
    volume = market.get("total_volumes", {}).get("usd", 0)
    rsi = 50  # fallback
    return {"price": price, "change_24h": change_24h, "volume": volume, "rsi": rsi}

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
        coins = response.json()[-50:]  # recent adds
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
                        hot_alerts.append(f"🧪 NEW COIN ALERT: '{coin['name']}' is up {change:.1f}% in 24h, vol ${volume:,.0f}")
            except:
                continue
    except:
        return []
    return hot_alerts

if st.button("🔁 Run Market Scan Now"):
    st.subheader(f"📊 Meme Coin Check — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for coin_id, name in COINS.items():
        try:
            data = get_price_data(coin_id)
            st.markdown(f"**{name}**: ${data['price']:.6f} | 24h: {data['change_24h']:.2f}% | Vol: ${data['volume']:,.0f}")
            if check_buy_signal(data):
                st.warning(f"🚨 BUY ALERT: {name} meets dip criteria!")
        except Exception as e:
            st.error(f"Error checking {name}: {e}")

    st.subheader("🧪 Scanning for New Hot Meme Coins...")
    new_alerts = find_hot_new_coins()
    if new_alerts:
        for alert in new_alerts:
            st.success(alert)
    else:
        st.info("No hot new coins found right now.")
