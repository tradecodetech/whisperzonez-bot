import os
import telebot
import openai
from flask import Flask, request

# === ENV VARIABLES ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://whisperzonez-bot.up.railway.app

# === INITIALIZATION ===
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# === HOME ROUTE (health check) ===
@app.route("/", methods=["GET"])
def index():
    return "🚦 WhisperZonez Bot is running!"

# === TELEGRAM WEBHOOK ENDPOINT ===
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "🚀 WhisperZonez KVFX Assistant is Online!")

# === BIAS COMMAND ===
@bot.message_handler(commands=['bias'])
def handle_bias(message):
    bot.send_message(message.chat.id, "📈 Bias: Range-bound with bullish undertone. Await CHoCH on H1.")

# === ALL OTHER MESSAGES — GPT REPLY ===
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    try:
        user_input = message.text
        bot.send_chat_action(message.chat.id, 'typing')

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are WhisperZonez, a smart money trading assistant."},
                {"role": "user", "content": user_input}
            ]
        )

        bot.reply_to(message, response.choices[0].message.content)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# === SET TELEGRAM WEBHOOK ===
def set_webhook():
    bot.remove_webhook()
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    success = bot.set_webhook(url=webhook_url)
    if success:
        print("✅ Webhook set successfully!")
    else:
        print("❌ Failed to set webhook.")

# === START SERVER ===
if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
