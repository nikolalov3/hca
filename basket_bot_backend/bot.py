import os
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

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
        await application.stop()
        await application.shutdown()


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


# Mount React static files
BUILD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'basket_bot_frontend', 'build')
if os.path.exists(BUILD_PATH):
    app.mount('/static', StaticFiles(directory=os.path.join(BUILD_PATH, 'static')), name='static')

@app.get('/')
async def serve_root():
    """Serve index.html for root path"""
    index_path = os.path.join(BUILD_PATH, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return HTMLResponse(f.read())
    return {"error": "Frontend not found"}

@app.get('/{path:path}')
async def serve_react(path: str):
    """Catch-all route to serve React app for client-side routing"""
    if path.startswith('api/') or path.startswith('webhook'):
        return {"error": "Not found"}
    # Serve index.html for all other routes
    index_path = os.path.join(BUILD_PATH, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return HTMLResponse(f.read())
    return {"error": "Frontend not found"}
            
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
