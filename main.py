# main.py – WhisperZonez x KVFX v3 Telegram AI Bot (Webhook Mode for Railway)

import os
import telebot
import openai
from flask import Flask, request
import base64

# === Load ENV Variables ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_CHAT_ID = os.getenv("DEFAULT_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# === Flask App for Webhook Handling ===
app = Flask(__name__)

@app.route('/')
def home():
    return "📡 WhisperZonez x KVFX AI Bot is Live (Webhook Mode)"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid request', 403

# === AI WhisperZonez Trading Reply ===
def get_whisperzonez_reply(user_input):
    prompt = f"""
You are WhisperZonez — a Tactical Whisper Mentor and KVFX Algo Assistant.
You interpret:
- Whisper candles (low body, high volume)
- Supply & demand zones with mitigation
- CHoCH and BOS
- KVFX v3 entries (green arrows)
- Volume traps, imbalances, trend context

Respond with clear, street-smart insight in a gritty, mentor-like tone.

User:
{user_input}

WhisperZonez:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# === Image Handler ===
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

# === Text Message Handler ===
@bot.message_handler(func=lambda msg: True)
def message_handler(message):
    try:
        reply = get_whisperzonez_reply(message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

# === Set Webhook When Starting ===
if __name__ == '__main__':
    webhook_url = os.getenv("WEBHOOK_URL")  # Must be your full Railway HTTPS domain
    if webhook_url:
        bot.remove_webhook()
        bot.set_webhook(url=f"{webhook_url}/webhook")
        print(f"✅ Webhook set to: {webhook_url}/webhook")
    app.run(host='0.0.0.0', port=8080)
