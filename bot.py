import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

import google.generativeai as genai

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

MAX_TELEGRAM_MESSAGE_LENGTH = 4096
MAX_GEMINI_REPLY_LENGTH = 8192

MENU, CEK_LOKER, CEK_ATS, TALK_HRD = range(4)

JOBSEEKER_QUESTIONS = [
    "1. Bagaimana cara membuat CV yang menarik?",
    "2. Apa saja yang harus dicantumkan dalam surat lamaran kerja?",
    "3. Bagaimana menghadapi interview kerja pertama kali?",
    "4. Apa saja pertanyaan yang sering muncul saat interview?",
    "5. Bagaimana menjawab pertanyaan tentang kelemahan diri?",
    "6. Bagaimana cara memperkenalkan diri saat interview?",
    "7. Apa itu CV ATS friendly?",
    "8. Bagaimana cara membuat CV yang lolos ATS?",
    "9. Apakah harus mencantumkan pengalaman organisasi di CV?",
    "10. Bagaimana menjawab pertanyaan soal gaji yang diharapkan?",
    "11. Bagaimana cara mencari lowongan kerja yang terpercaya?",
    "12. Apa tanda-tanda lowongan kerja penipuan?",
    "13. Bagaimana cara follow up lamaran kerja yang sudah dikirim?",
    "14. Apakah perlu membuat LinkedIn untuk melamar kerja?",
    "15. Bagaimana cara menghadapi psikotes kerja?",
    "16. Bagaimana menulis email lamaran kerja yang baik?",
    "17. Apakah perlu membuat portfolio? Bagaimana caranya?",
    "18. Bagaimana jika tidak punya pengalaman kerja?",
    "19. Bagaimana menulis surat pengunduran diri yang sopan?",
    "20. Apa saja dokumen yang biasanya diminta saat melamar kerja?",
    "21. Bagaimana cara menyesuaikan CV dengan posisi yang dilamar?",
    "22. Bagaimana cara membangun networking untuk mencari kerja?",
    "23. Bagaimana memperbaiki CV yang sering ditolak?",
    "24. Bagaimana menghadapi pertanyaan tentang gap/jeda waktu di CV?",
    "25. Bagaimana menjawab jika ditanya alasan resign dari pekerjaan sebelumnya?",
    "26. Bagaimana jika diminta gaji di bawah standar?",
    "27. Apakah boleh melamar lebih dari satu posisi di perusahaan yang sama?",
    "28. Bagaimana cara riset perusahaan sebelum interview?",
    "29. Apa saja soft skill yang dibutuhkan di dunia kerja?",
    "30. Bagaimana menghadapi penolakan setelah interview?",
]

HRD_QUESTIONS = [
    "1. Ceritakan tentang diri Anda.",
    "2. Apa motivasi Anda melamar di perusahaan ini?",
    "3. Apa kelebihan yang Anda miliki?",
    "4. Apa kelemahan Anda?",
    "5. Apa pencapaian terbesar Anda sejauh ini?",
    "6. Bagaimana Anda mengatasi konflik di tempat kerja?",
    "7. Kenapa kami harus menerima Anda?",
    "8. Apa yang Anda ketahui tentang perusahaan ini?",
    "9. Apa tujuan karir Anda 5 tahun ke depan?",
    "10. Bagaimana cara Anda bekerja dalam tim?",
    "11. Bagaimana mengatur waktu dan prioritas kerja?",
    "12. Bagaimana menghadapi tekanan di tempat kerja?",
    "13. Mengapa Anda resign dari pekerjaan sebelumnya?",
    "14. Apa yang Anda lakukan selama gap/jeda waktu di CV Anda?",
    "15. Apakah Anda bersedia ditempatkan di luar kota?",
    "16. Bagaimana menangani tugas yang belum pernah Anda lakukan sebelumnya?",
    "17. Bagaimana Anda memotivasi diri sendiri di tempat kerja?",
    "18. Apakah Anda punya pertanyaan untuk kami?",
    "19. Seberapa besar ekspektasi gaji Anda?",
    "20. Bagaimana Anda menyesuaikan diri dengan lingkungan baru?",
    "21. Bagaimana Anda menyelesaikan pekerjaan dengan deadline ketat?",
    "22. Apakah Anda memiliki pengalaman memimpin tim?",
    "23. Bagaimana Anda menangani kritik dari rekan kerja atau atasan?",
    "24. Bagaimana jika Anda tidak setuju dengan keputusan atasan?",
    "25. Apakah Anda mengikuti perkembangan industri/teknologi terbaru?",
    "26. Bagaimana Anda menjaga profesionalisme di tempat kerja?",
    "27. Bagaimana Anda memastikan pekerjaan Anda berkualitas?",
    "28. Apakah Anda pernah gagal? Bagaimana cara mengatasinya?",
    "29. Apa yang Anda lakukan untuk meningkatkan skill?",
    "30. Bagaimana sikap Anda terhadap perubahan di perusahaan?",
]

# Ganti menu utama ke huruf A, B, C, D
MENU_KEYBOARD = [
    ["A. Pertanyaan Pencari Kerja", "B. Pertanyaan HRD"],
    ["C. Cek Loker", "D. Cek CV ATS"],
    ["E. Berbicara dengan Asisten IKJ"]
]

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo, saya Assisten AI IKJ2018. Silakan pilih menu berikut:",
        reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
    )
    return MENU

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if text.startswith("a"):
        await send_long_message(update, "Berikut 30 pertanyaan umum dari pencari kerja (Jobseeker):\n\n" + "\n".join(JOBSEEKER_QUESTIONS))
        await update.message.reply_text("Ketikkan nomor pertanyaan untuk mendapatkan solusi/jawaban dari Assisten AI IKJ2018, atau ketik /menu untuk kembali ke menu utama.")
        context.user_data['last_menu'] = "jobseeker"
        return MENU
    elif text.startswith("b"):
        await send_long_message(update, "Berikut 30 pertanyaan umum dari HRD beserta cara menjawabnya:\n\n" + "\n".join(HRD_QUESTIONS))
        await update.message.reply_text("Ketikkan nomor pertanyaan HRD untuk mendapatkan contoh jawaban dari Assisten AI IKJ2018, atau ketik /menu untuk kembali ke menu utama.")
        context.user_data['last_menu'] = "hrd"
        return MENU
    elif text.startswith("c"):
        await update.message.reply_text(
            "Silakan kirimkan data teks lowongan kerja yang ingin dicek keaslian/keamanannya. Assisten AI IKJ2018 akan membantu mengecek apakah loker tersebut real atau palsu."
        )
        return CEK_LOKER
    elif text.startswith("d"):
        await update.message.reply_text(
            "Silakan copy-paste CV Anda dalam bentuk teks ke sini. Assisten AI IKJ2018 akan membantu mengecek apakah CV sudah ATS friendly dan memberikan saran perbaikan."
        )
        return CEK_ATS
    elif text.startswith("e"):
        await update.message.reply_text(
            "Anda dapat langsung mengetikkan pertanyaan seputar HRD, karir, interview, CV, atau rekrutmen. Assisten AI IKJ2018 siap menjawab pertanyaan Anda sebagai konsultan HRD. Ketik /menu untuk kembali ke menu utama."
        )
        return TALK_HRD
    else:
        await show_menu(update, context)
        return MENU

async def pertanyaan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_choice = context.user_data.get('last_menu', '')
    try:
        q_num = int(update.message.text.strip())
    except Exception:
        q_num = None
    if menu_choice == "jobseeker" and q_num and 1 <= q_num <= 30:
        question = JOBSEEKER_QUESTIONS[q_num - 1]
        prompt = f"Sebagai konsultan HRD profesional, berikan jawaban atau solusi singkat yang praktis, profesional, dan memberi semangat atas pertanyaan berikut: {question}"
        await gemini_reply(update, prompt)
    elif menu_choice == "hrd" and q_num and 1 <= q_num <= 30:
        question = HRD_QUESTIONS[q_num - 1]
        prompt = f"Sebagai konsultan HRD profesional, berikan contoh cara menjawab pertanyaan interview berikut beserta tips suksesnya: {question}"
        await gemini_reply(update, prompt)
    else:
        await update.message.reply_text("Nomor pertanyaan tidak valid atau belum memilih menu. Ketik /menu untuk kembali ke menu utama.")
    return MENU

async def cek_loker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loker_text = update.message.text
    prompt = (
        f"Berikut adalah teks lowongan kerja:\n\n{loker_text}\n\n"
        "Sebagai Assisten AI IKJ2018, cek apakah loker di atas termasuk loker asli atau penipuan, "
        "berikan alasan dan saran atau peringatan yang jelas kepada pencari kerja."
    )
    await gemini_reply(update, prompt)
    await update.message.reply_text("Ketik /menu untuk kembali ke menu utama.")
    return MENU

async def cek_ats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cv_text = update.message.text
    prompt = (
        f"Berikut adalah isi CV:\n\n{cv_text[:3500]}\n\n"
        "Sebagai Assisten AI IKJ2018, cek apakah CV di atas sudah ATS friendly. "
        "Berikan analisa, perbaikan, dan tambahan yang perlu diperbaiki agar CV lolos ATS."
    )
    await gemini_reply(update, prompt)
    await update.message.reply_text("Ketik /menu untuk kembali ke menu utama.")
    return MENU

async def talk_hrd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    prompt = (
        f"Sebagai Assisten AI IKJ2018 dan konsultan HRD profesional, jawablah pertanyaan berikut secara ramah, profesional, dan informatif:\n\n{user_message}"
    )
    await gemini_reply(update, prompt)
    return TALK_HRD

async def gemini_reply(update: Update, prompt: str):
    await update.message.chat.send_action(action="typing")
    try:
        response = model.generate_content(prompt)
        text = response.text.strip() if hasattr(response, "text") else "Mohon maaf, tidak ada jawaban."
        text = text[:MAX_GEMINI_REPLY_LENGTH]
        await send_long_message(update, f"Assisten AI IKJ2018:\n\n{text}")
    except Exception as e:
        await update.message.reply_text(f"Assisten AI IKJ2018 gagal menjawab: {e}")

async def send_long_message(update: Update, text: str):
    for i in range(0, len(text), MAX_TELEGRAM_MESSAGE_LENGTH):
        await update.message.reply_text(text[i:i+MAX_TELEGRAM_MESSAGE_LENGTH])

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_menu(update, context)

async def group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = context.bot.username
    if update.message and update.message.text and ('@' + bot_username) in update.message.text:
        await show_menu(update, context)
        return MENU

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, show_menu),
            CommandHandler("menu", menu_command),
            MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_handler),
        ],
        states={
            MENU: [
                MessageHandler(filters.Regex(r"^\d+$"), pertanyaan_handler),
                MessageHandler(filters.TEXT & (~filters.COMMAND), menu_handler),
            ],
            CEK_LOKER: [MessageHandler(filters.TEXT & (~filters.COMMAND), cek_loker_handler)],
            CEK_ATS: [MessageHandler(filters.TEXT & (~filters.COMMAND), cek_ats_handler)],
            TALK_HRD: [MessageHandler(filters.TEXT & (~filters.COMMAND), talk_hrd_handler)],
        },
        fallbacks=[CommandHandler("menu", menu_command)],
    )
    application.add_handler(conv_handler)
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()