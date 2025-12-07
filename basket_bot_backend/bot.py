import os
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏀 GRAJ W KOSZA", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Siemano! Gotowy na mecz? Kliknij poniżej, żeby otworzyć apkę:",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot wystartował! Czeka na wiadomości...")
    app.run_polling()
