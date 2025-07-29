import telebot
import openai
import os
from flask import Flask, request

# === ENV VARIABLES ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === BOT SETUP ===
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# === FLASK APP (FOR WEBHOOK MODE IF NEEDED) ===
app = Flask(__name__)

@app.route('/')
def index():
    return "WhisperZonez KVFX Assistant is running."

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, """
🎯 *WhisperZonez KVFX Assistant Activated*

🛰️ *TACTICAL SYSTEMS ONLINE*

*Core Commands:*
• /analyze - Send chart for tactical analysis  
• /bias - Get current market bias  
• /kvfxbias - KVFX v3 tactical analysis  
• /kvfxbias_weekly - Weekly market outlook  
• /logtrade - Log a new trade  
• /stats - View trading performance  
• /webhook - TradingView integration setup  
• /help - Full command reference

*Systems Status:*
✅ TradingView Integration  
✅ Chart Analysis (Vision AI)  
✅ Auto Alerts  
✅ KVFX Algorithm

Drop a chart, ask a question, or share a setup.  
*WhisperZonez is ready.*
""", parse_mode='Markdown')

# === BIASSHORT COMMAND EXAMPLE ===
@bot.message_handler(commands=['bias'])
def bias_handler(message):
    bot.reply_to(message, "📊 WhisperZonez Market Bias: Neutral to Bullish | Waiting for CHoCH confirmation.")

# === OPENAI INTEGRATED RESPONSE ===
@bot.message_handler(func=lambda message: True)
def ai_response_handler(message):
    user_input = message.text
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or use "gpt-3.5-turbo" if preferred
            messages=[
                {"role": "system", "content": "You are WhisperZonez, a professional smart money and order flow analyst assistant. Answer questions about CHoCH, BOS, mitigation blocks, liquidity sweeps, and institutional trading like a trading coach."},
                {"role": "user", "content": user_input}
            ]
        )

        reply = response['choices'][0]['message']['content']
        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"⚠️ WhisperZonez Error: {str(e)}")

# === LOCAL DEV MODE ===
if __name__ == "__main__":
    print("📡 WhisperZonez KVFX Assistant is LIVE")
    bot.polling(non_stop=T_
