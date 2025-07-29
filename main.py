import os
import telebot
import openai
from flask import Flask, request, jsonify

# === ENV VARIABLES ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # Optional: your personal Telegram ID

# === INITIALIZATION ===
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# === ROOT HEALTH CHECK ===
@app.route('/')
def home():
    return "WhisperZonez Assistant: ONLINE"

# === TRADINGVIEW WEBHOOK RECEIVER ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    try:
        symbol = data.get("ticker", "Unknown Symbol")
        alert = data.get("alert", "No alert text")
        timeframe = data.get("timeframe", "N/A")

        message = f"""
📡 *TradingView Webhook Alert Received*  
🔹 Symbol: `{symbol}`  
🕒 Timeframe: `{timeframe}`  
📢 Alert: `{alert}`  
"""

        # Send to admin or a channel
        if ADMIN_CHAT_ID:
            bot.send_message(ADMIN_CHAT_ID, message, parse_mode='Markdown')
        else:
            print("No ADMIN_CHAT_ID set.")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, """
🚀 *WhisperZonez KVFX Assistant Activated*

🎯 Tactical Systems Online

Commands:
/analyze - Send chart for tactical analysis  
/bias - Get market bias  
/kvfxbias - KVFX tactical analysis  
/logtrade - Log a trade  
/webhook - Setup TradingView alerts  
/help - Full command reference

✅ Chart AI | ✅ Alerts | ✅ KVFX Algo Ready
""", parse_mode='Markdown')

# === MARKET BIAS COMMAND ===
@bot.message_handler(commands=['bias'])
def bias_handler(message):
    bot.reply_to(message, "📈 Current Bias: Range-bound with bullish undertone. Await CHoCH on H1.")

# === GPT AI RESPONSE LOGIC ===
@bot.message_handler(func=lambda msg: True)
def whisper_ai_handler(message):
    user_input = message.text
    try:
        bot.send_chat_action(message.chat.id, 'typing')

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are WhisperZonez, a smart money trader assistant who explains CHoCH, BOS, liquidity sweeps, mitigation, etc., like a seasoned order flow coach."},
                {"role": "user", "content": user_input}
            ]
        )

        reply = response['choices'][0]['message']['content']
        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# === LOCAL DEV ===
if __name__ == "__main__":
    print("🚦 WhisperZonez Assistant Running")
    bot.polling(non_stop=True)
