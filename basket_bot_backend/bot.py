import os
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # np. https://twoja-domena.railway.app
PORT = 8080

app = FastAPI()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 Otwórz aplikację", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Oto twoja aplikacja! Kliknij poniżej aby ją otworzyć:",
        reply_markup=reply_markup
    )

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # Ustaw webhook
    
    
    if WEBHOOK_URL:
                await application.bot.delete_webhook(drop_pending_updates=True)
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    
    return application

application = None

@app.on_event("startup")
async def startup():
    global application
    application = await main()
    print(f"Bot has been started! Webhook: {WEBHOOK_URL}/webhook")

@app.post("/webhook")
async def webhook(update: dict):
    global application
    if application:
        telegram_update = Update.de_json(update, application.bot)
        await application.process_update(telegram_update)
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

    if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
