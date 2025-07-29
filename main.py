# main.py – Multifunction AI Telegram Bot with WhisperZonez + OpenAI Logic

import os
import telebot
import openai
from flask import Flask, request
import threading
import base64

# === Load ENV Variables ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_CHAT_ID = os.getenv("DEFAULT_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# === Flask App ===
app = Flask(__name__)

@app.route('/')
def home():
    return "📡 WhisperZonez AI Assistant is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data:
        alert_message = data.get("message", "📊 KVFX Alert Received")
        bot.send_message(DEFAULT_CHAT_ID, alert_message)
        return "ok", 200
    return "no data", 400

# === AI Logic ===
def whisperzonez_response(user_input):
    system_prompt = """
You are WhisperZonez, a gritty and tactical KVFX mentor. You specialize in:
- Whisper candles (low body, high volume)
- CHoCH and BOS confirmations
- Mitigation zones and imbalance fills
- Trend context using KVFX v3 logic

Speak with clarity, edge, and a bit of trader street wisdom.
"""
    return call_openai(user_input, system_prompt)

def general_assistant_response(user_input):
    system_prompt = "You are a helpful, smart AI assistant helping a trader and entrepreneur with business, strategy, and technology questions."
    return call_openai(user_input, system_prompt)

def call_openai(user_input, system_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()

# === Telegram Handlers ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Welcome to WhisperZonez AI Assistant ⚙️\n\nSend /whisper for trade zone logic.\nSend /ask for general AI help.\nSend a chart photo to analyze.")

@bot.message_handler(commands=['whisper'])
def handle_whisper(message):
    bot.reply_to(message, "🎯 Drop your question about trading zones, CHoCH, or whisper candles.")

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    bot.reply_to(message, "💡 Send your question and I’ll assist you like a personal AI coach.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        image_b64 = base64.b64encode(downloaded).decode('utf-8')

        vision_prompt = [
            {"type": "text", "text": "Analyze this chart with CHoCH, BOS, Whisper candles, and trend zones."},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_b64}}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[{"role": "user", "content": vision_prompt}],
            max_tokens=500
        )
        output = response.choices[0].message.content.strip()
        bot.reply_to(message, f"📉 Chart Analysis:\n{output}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error analyzing image: {e}")

@bot.message_handler(func=lambda msg: True)
def handle_all_messages(message):
    user_text = message.text.lower()

    if '/whisper' in user_text:
        reply = whisperzonez_response(message.text)
    elif '/ask' in user_text:
        reply = general_assistant_response(message.text)
    else:
        reply = whisperzonez_response(message.text)

    bot.reply_to(message, reply)

# === Launch Bot and Webhook ===
def run_web():
    from telebot import apihelper
    webhook_url = f"https://{os.getenv('RAILWAY_STATIC_URL') or 'whisperzonez-bot.up.railway.app'}/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    run_web()
