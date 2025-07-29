import os
import telebot
from flask import Flask, request

# Load token from environment variable
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables.")

# Create Flask app and TeleBot instance
app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Telegram message handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "📡 WhisperZonez x KVFX Assistant is live and ready.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "👋 You said: " + message.text)

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# Webhook setup and server launch
if __name__ == '__main__':
    webhook_url = "https://whisperzonez-bot.up.railway.app/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")
    app.run(host="0.0.0.0", port=8080)
