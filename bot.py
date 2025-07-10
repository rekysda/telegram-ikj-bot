import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

import google.generativeai as genai

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
MAX_TELEGRAM_MESSAGE_LENGTH = 4096

MENU, CEK_LOKER, CEK_ATS, TALK_HRD = range(4)

JOBSEEKER_QUESTIONS = [
    # ... (list pertanyaan jobseeker, sama seperti sebelumnya)
]
HRD_QUESTIONS = [
    # ... (list pertanyaan HRD, sama seperti sebelumnya)
]

MENU_KEYBOARD = [
    ["1. Pertanyaan Pencari Kerja", "2. Pertanyaan HRD"],
    ["3. Cek Loker", "4. Cek CV ATS"],
    ["5. Berbicara dengan Asisten IKJ"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo, saya Assisten AI IKJ2018. Silakan pilih menu berikut:",
        reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text.startswith("1"):
        await send_long_message(update, "Berikut 30 pertanyaan umum dari pencari kerja (Jobseeker):\n\n" + "\n".join(JOBSEEKER_QUESTIONS))
        await update.message.reply_text("Ketikkan nomor pertanyaan untuk mendapatkan solusi/jawaban dari Assisten AI IKJ2018, atau ketik /menu untuk kembali ke menu utama.")
        context.user_data['last_menu'] = "jobseeker"
        return MENU
    elif text.startswith("2"):
        await send_long_message(update, "Berikut 30 pertanyaan umum dari HRD beserta cara menjawabnya:\n\n" + "\n".join(HRD_QUESTIONS))
        await update.message.reply_text("Ketikkan nomor pertanyaan HRD untuk mendapatkan contoh jawaban dari Assisten AI IKJ2018, atau ketik /menu untuk kembali ke menu utama.")
        context.user_data['last_menu'] = "hrd"
        return MENU
    elif text.startswith("3"):
        await update.message.reply_text(
            "Silakan kirimkan data teks lowongan kerja yang ingin dicek keaslian/keamanannya. Assisten AI IKJ2018 akan membantu mengecek apakah loker tersebut real atau palsu."
        )
        return CEK_LOKER
    elif text.startswith("4"):
        await update.message.reply_text(
            "Silakan copy-paste CV Anda dalam bentuk teks ke sini. Assisten AI IKJ2018 akan membantu mengecek apakah CV sudah ATS friendly dan memberikan saran perbaikan."
        )
        return CEK_ATS
    elif text.startswith("5"):
        await update.message.reply_text(
            "Anda dapat langsung mengetikkan pertanyaan seputar HRD, karir, interview, CV, atau rekrutmen. Assisten AI IKJ2018 siap menjawab pertanyaan Anda sebagai konsultan HRD. Ketik /menu untuk kembali ke menu utama."
        )
        return TALK_HRD
    else:
        await update.message.reply_text(
            "Menu tidak dikenali. Silakan pilih dari menu yang tersedia.",
            reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
        )
        return MENU

# ... (handler lain tetap sama)

async def cek_ats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User mengirimkan CV dalam bentuk teks
    cv_text = update.message.text
    prompt = (
        f"Berikut adalah isi CV:\n\n{cv_text[:3500]}\n\n"
        "Sebagai Assisten AI IKJ2018, cek apakah CV di atas sudah ATS friendly. "
        "Berikan analisa, perbaikan, dan tambahan yang perlu diperbaiki agar CV lolos ATS."
    )
    await gemini_reply(update, prompt)
    await update.message.reply_text("Ketik /menu untuk kembali ke menu utama.")
    return MENU

# ... (fungsi send_long_message, gemini_reply, menu_command, dan main tetap sama)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("menu", menu_command)],
        states={
            MENU: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND),
                    menu_handler
                ),
                MessageHandler(
                    filters.Regex(r"^\d+$"), 
                    pertanyaan_handler
                ),
            ],
            CEK_LOKER: [MessageHandler(filters.TEXT & (~filters.COMMAND), cek_loker_handler)],
            CEK_ATS: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), cek_ats_handler)
            ],
            TALK_HRD: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), talk_hrd_handler)
            ],
        },
        fallbacks=[CommandHandler("menu", menu_command)],
    )

    application.add_handler(conv_handler)
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()