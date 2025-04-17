import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = "7918867983:AAEm--XCS-FUvje0A4ZhY2aKNgsr0ZDvVIw"
FLASK_API_URL = "http://127.0.0.1:5000/chatbot_api/"  # Your Flask API URL

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm your College Chatbot.")

async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    response = requests.post(FLASK_API_URL, json={"message": user_message})
    bot_response = response.json().get("response", "Sorry, I didn't understand that.")
    await update.message.reply_text(bot_response)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
