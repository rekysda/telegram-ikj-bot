import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

MAX_TELEGRAM_MESSAGE_LENGTH = 4096

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Halo! Saya asisten lowongan kerja berbasis Gemini AI. Silakan tanya apa saja.'
    )

async def ask_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    try:
        response = model.generate_content(user_message)
        # Ambil teks jawaban dari response
        text = response.text.strip() if hasattr(response, "text") else "Mohon maaf, tidak ada jawaban."
        # Kirim dalam beberapa bagian jika terlalu panjang
        for i in range(0, len(text), MAX_TELEGRAM_MESSAGE_LENGTH):
            await update.message.reply_text(text[i:i+MAX_TELEGRAM_MESSAGE_LENGTH])
    except Exception as e:
        await update.message.reply_text(f"Gagal menghubungi Gemini: {e}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    # Untuk semua pesan teks, kirim ke Gemini
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ask_gemini))
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()