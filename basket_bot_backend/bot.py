import os
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = 8080

app = FastAPI()
application = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Open App", web_app=WebAppInfo(url=WEBAPP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click button to open:", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "/start - Open app\n/help - Show this message"
    await update.message.reply_text(help_text)


async def init_bot():
    global application
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
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
    print(f"Bot started! Webhook: {WEBHOOK_URL}/webhook")


@app.on_event("shutdown")
async def shutdown():
    pass


@app.post("/webhook")
async def webhook(update: dict):
    global application
    if application:
        try:
            telegram_update = Update.de_json(update, application.bot)
            await application.process_update(telegram_update)
        except Exception as e:
            print(f"Error: {e}")
    return JSONResponse({"ok": True})


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reset-webhook")
async def reset_webhook():
    global application
    if application and WEBHOOK_URL:
        try:
            await application.bot.delete_webhook(drop_pending_updates=False)
            await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
            webhook_info = await application.bot.get_webhook_info()
            return {
                "status": "success",
                "message": "Webhook reset",
                "webhook_url": webhook_info.url,
                "pending_updates": webhook_info.pending_update_count
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"error": "Not initialized"}


@app.get("/")
async def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Basket Bot</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
            .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-top: 0; }
            p { color: #666; text-align: center; }
            .status { background: #f9f9f9; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; }
            .status-title { font-weight: bold; margin-bottom: 10px; }
            .status-item { margin: 8px 0; font-size: 14px; }
            button { padding: 10px 20px; margin: 10px 0; width: 100%; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; font-weight: bold; }
            .btn-primary { background: #667eea; color: white; }
            .btn-primary:hover { background: #5568d3; }
            .btn-secondary { background: #e0e0e0; color: #333; }
            .btn-secondary:hover { background: #d0d0d0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Basket Bot</h1>
            <p>Telegram Application</p>
            
            <div class="status">
                <div class="status-title">Status</div>
                <div class="status-item">Backend: Online</div>
                <div class="status-item" id="tg-status">Telegram: Waiting</div>
                <div class="status-item" id="user-status">User: Not connected</div>
            </div>
            
            <button class="btn-primary" onclick="openApp()">Open App</button>
            <button class="btn-secondary" onclick="resetWebhook()">Reset Webhook</button>
            
            <p style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">Basket Bot v1.0</p>
        </div>

        <script>
            function initTelegram() {
                if (window.Telegram && window.Telegram.WebApp) {
                    var tg = window.Telegram.WebApp;
                    tg.ready();
                    document.getElementById('tg-status').textContent = 'Telegram: Connected';
                    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                        var user = tg.initDataUnsafe.user;
                        document.getElementById('user-status').textContent = 'User: ' + (user.first_name || 'Unknown');
                    }
                }
            }

            function openApp() {
                if (window.Telegram && window.Telegram.WebApp) {
                    window.Telegram.WebApp.expand();
                }
            }

            function resetWebhook() {
                fetch('/reset-webhook', { method: 'POST' })
                    .then(function(response) {
                        if (response.ok) {
                            alert('Webhook reset!');
                        } else {
                            alert('Error');
                        }
                    })
                    .catch(function(error) {
                        alert('Failed');
                    });
            }

            window.addEventListener('load', initTelegram);
            initTelegram();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
