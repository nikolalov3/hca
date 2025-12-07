import os
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from pathlib import Path

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # np. https://twoja-domena.railway.app
PORT = 8080

app = FastAPI()
application = None  # Global variable to store the bot application


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 Otwórz aplikację", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Oto twoja aplikacja! Kliknij poniżej aby ją otworzyć:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Dostępne komendy:\n"
        "/start - Otwórz aplikację\n"
        "/help - Wyświetl tę wiadomość"
    )
    await update.message.reply_text(help_text)


async def init_bot():
    """Initialize the Telegram bot application"""
    global application
    
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Ustaw webhook
    if WEBHOOK_URL:
        await application.bot.delete_webhook(drop_pending_updates=True)
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        print(f"Bot webhook set to: {WEBHOOK_URL}/webhook")
    
    await application.initialize()
    return application


@app.on_event("startup")
async def startup():
    global application
    application = await init_bot()
    print(f"Bot has been started! Webhook: {WEBHOOK_URL}/webhook")


@app.on_event("shutdown")
async def shutdown():
    global application
    if application:
        pass

@app.post("/webhook")
async def webhook(update: dict):
    global application
    if application:
        try:
            telegram_update = Update.de_json(update, application.bot)
            await application.process_update(telegram_update)
        except Exception as e:
            print(f"Error processing update: {e}")
    return JSONResponse({"ok": True})


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/reset-webhook")
async def reset_webhook():
    """Force reset webhook to Railway URL - use this to migrate from ngrok"""
    global application
    if application and WEBHOOK_URL:
        try:
            # Delete old webhook first
            await application.bot.delete_webhook(drop_pending_updates=False)
            # Set new webhook
            await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
            webhook_info = await application.bot.get_webhook_info()
            return {
                "status": "success",
                "message": "Webhook reset successfully",
                "webhook_url": webhook_info.url,
                "pending_updates": webhook_info.pending_update_count
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"error": "application not initialized or WEBHOOK_URL not set"}




from fastapi.staticfiles import StaticFiles
static_dir = Path(__file__).parent.parent / "basket_bot_frontend" / "build"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
uvicorn.run(app, host="0.0.0.0", port=PORT)
