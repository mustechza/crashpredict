import time
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from telegram import Bot

# === Telegram Bot Setup ===
TELEGRAM_TOKEN = "<YOUR_TOKEN>"
CHAT_ID = "<YOUR_CHAT_ID>"
bot = Bot(token=TELEGRAM_TOKEN)

# === Fetch Price Data ===
def fetch_binance_candles(symbol='BTCUSDT', interval='1m', limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df["close"] = df["close"].astype(float)
    return df[["timestamp", "close"]]

# === Calculate RSI ===
def calculate_rsi(df, period=14):
    rsi = RSIIndicator(close=df["close"], window=period)
    df["RSI"] = rsi.rsi()
    return df

# === Send Telegram Alert ===
def send_alert(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

# === Main Signal Logic ===
def check_signal():
    df = fetch_binance_candles()
    df = calculate_rsi(df)
    latest_rsi = df["RSI"].iloc[-1]
    
    if latest_rsi > 70:
        msg = f"🔴 SELL SIGNAL — RSI: {latest_rsi:.2f}"
        send_alert(msg)
    elif latest_rsi < 30:
        msg = f"🟢 BUY SIGNAL — RSI: {latest_rsi:.2f}"
        send_alert(msg)
    else:
        print(f"🟡 RSI: {latest_rsi:.2f} — No signal")

# === Loop Every X Seconds ===
while True:
    try:
        check_signal()
    except Exception as e:
        print("⚠️ Error:", e)
    time.sleep(60)  # Wait 60 seconds before next check
