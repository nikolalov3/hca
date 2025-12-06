from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# WKLEJ SWÓJ PRAWDZIWY TOKEN PONIŻEJ (w cudzysłowie)
TOKEN = "8353950120:AAExoG7jNlgLaM3ngovzCwVOyY8bLsG0deU" 
# To jest Twój adres z ngroka (ze zdjęcia)
WEBAPP_URL = "https://rae-beachless-zane.ngrok-free.dev"

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

