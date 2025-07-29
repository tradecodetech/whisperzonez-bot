# main.py - WhisperZonez + KVFX v3 Telegram AI Bot (for Railway Hosting)

import os
import telebot
import openai
from flask import Flask, request
import threading
import base64

# === Load ENV variables ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
print("🚨 TELEGRAM_TOKEN:", TELEGRAM_TOKEN)
if TELEGRAM_TOKEN is None:
    raise Exception("❌ TELEGRAM_TOKEN is missing. Check Railway environment variables.")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_CHAT_ID = os.getenv("DEFAULT_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
bot.remove_webhook()  # Clear old webhook if any
bot.set_webhook(url="https://whisperzonez-bot.up.railway.app/webhook")
openai.api_key = OPENAI_API_KEY

# === Flask App for Webhook Support ===
app = Flask(__name__)

@app.route('/')
def home():
    return "WhisperZonez AI Bot is Live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data:
        alert_message = data.get("message", "KVFX Signal Alert")
        chat_id = DEFAULT_CHAT_ID
        if chat_id:
            bot.send_message(chat_id, f"📈 {alert_message}")
        return "ok", 200
    return "no data", 400

# === AI Whisper + KVFX Response Generator ===
def get_whisperzonez_reply(user_input):
    prompt = f"""
You are WhisperZonez — a Tactical Whisper Mentor and KVFX Algo Assistant.
You interpret:
- Whisper candles (low body, high volume)
- Supply & demand zones with mitigation
- CHoCH (Change of Character) and BOS (Break of Structure)
- Green arrow entries from KVFX v3 logic
- Volume traps, imbalance fills, and trend context

Respond to user input with clear, concise, tactical trading insight.
Tone: Street-smart, gritty, and mentor-like. Use emojis if helpful.

User:
{user_input}

WhisperZonez:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# === Telegram Commands & Handlers ===
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, "📡 WhisperZonez x KVFX Assistant ready. Send a question, chart screenshot, or zone logic setup.")

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_b64 = base64.b64encode(downloaded_file).decode('utf-8')

        vision_prompt = [
            {"type": "text", "text": "Analyze this trading chart using WhisperZonez logic: CHoCH, BOS, whisper candle zones, mitigation, and KVFX trend entries."},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_b64}}
        ]

        result = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[{"role": "user", "content": vision_prompt}],
            max_tokens=500
        )
        output = result.choices[0].message.content.strip()
        bot.reply_to(message, f"🧠 Chart Insight:\n{output}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error analyzing image: {e}")

@bot.message_handler(func=lambda msg: True)
def message_handler(message):
    user_text = message.text
    try:
        reply = get_whisperzonez_reply(user_text)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Error generating response: {e}")

# === Launch Both Bot and Flask ===
def run_bot():
    print("Webhook started...")
    bot.remove_webhook()
    bot.set_webhook(url="https://your-railway-app-name.up.railway.app/webhook")

def run_web():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    threading.Thread(target=run_bot).start()
