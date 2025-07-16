
# PATCHED: v6.1.5a
# Fix: Safe defaults in gpt_score for missing change or volume
# Ensures all selected meme coins render even with partial data

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
