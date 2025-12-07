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
    keyboard = [[InlineKeyboardButton("Otworz aplikacje", web_app=WebAppInfo(url=WEBAPP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Klikni przycisk poniżej aby otworzyć aplikację:", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "/start - Otwórz aplikację\\n/help - Pokaż tę wiadomość"
    await update.message.reply_text(help_text)

async def init_bot():
    global application
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    if WEBHOOK_URL:
        await application.bot.delete_webhook(drop_pending_updates=True)
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        print(f"Bot webhook ustawiony na: {WEBHOOK_URL}/webhook")
    
    await application.initialize()
    return application

@app.on_event("startup")
async def startup():
    global application
    application = await init_bot()
    print(f"Bot uruchomiony! Webhook: {WEBHOOK_URL}/webhook")

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
            print(f"Blad: {e}")
    return JSONResponse({"ok": True})

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hoop Connect - Koszyk</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                padding: 20px;
                border-bottom: 2px solid #667eea;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            .header h1 {
                color: #667eea;
                font-size: 28px;
                margin-bottom: 5px;
            }
            .header p {
                color: #999;
                font-size: 14px;
            }
            .container {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }
            .product-card {
                background: white;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .product-info h3 {
                color: #333;
                font-size: 16px;
                margin-bottom: 5px;
            }
            .product-info p {
                color: #999;
                font-size: 13px;
            }
            .product-price {
                color: #667eea;
                font-weight: bold;
                font-size: 18px;
            }
            .cart-info {
                background: rgba(255, 255, 255, 0.95);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 15px;
                text-align: center;
            }
            .cart-total {
                font-size: 24px;
                color: #667eea;
                font-weight: bold;
                margin: 10px 0;
            }
            .button-group {
                display: flex;
                gap: 10px;
                padding: 20px;
                background: rgba(255, 255, 255, 0.95);
                border-top: 2px solid #667eea;
            }
            button {
                flex: 1;
                padding: 15px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .btn-add {
                background: #667eea;
                color: white;
            }
            .btn-add:active {
                background: #5568d3;
                transform: scale(0.98);
            }
            .btn-checkout {
                background: #48bb78;
                color: white;
            }
            .btn-checkout:active {
                background: #38a169;
                transform: scale(0.98);
            }
            .empty-cart {
                text-align: center;
                color: white;
                padding: 40px;
            }
            .empty-cart svg {
                width: 80px;
                height: 80px;
                margin-bottom: 20px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Hoop Connect</h1>
            <p>Aplikacja handlowa</p>
        </div>
        
        <div class="container">
            <div class="cart-info">
                <p>Twoj Koszyk</p>
                <div class="cart-total" id="cart-total">0 PLN</div>
                <p style="color: #999; font-size: 12px;" id="cart-items">0 produktów</p>
            </div>
            
            <div id="products-list">
                <div class="product-card">
                    <div class="product-info">
                        <h3>Produkt 1</h3>
                        <p>Wysokiej jakosci towar</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="product-price">49.99 PLN</div>
                        <button class="btn-add" onclick="addToCart('Produkt 1', 49.99)">Dodaj</button>
                    </div>
                </div>
                
                <div class="product-card">
                    <div class="product-info">
                        <h3>Produkt 2</h3>
                        <p>Premium wersja</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="product-price">79.99 PLN</div>
                        <button class="btn-add" onclick="addToCart('Produkt 2', 79.99)">Dodaj</button>
                    </div>
                </div>
                
                <div class="product-card">
                    <div class="product-info">
                        <h3>Produkt 3</h3>
                        <p>Specjalna oferta</p>
                    </div>
                    <div style="text-align: right;">
                        <div class="product-price">29.99 PLN</div>
                        <button class="btn-add" onclick="addToCart('Produkt 3', 29.99)">Dodaj</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="button-group">
            <button class="btn-checkout" onclick="checkout()">Zakoncz Zakupy</button>
        </div>
        
        <script>
            let cart = [];
            
            function initTelegram() {
                if (window.Telegram && window.Telegram.WebApp) {
                    window.Telegram.WebApp.ready();
                    window.Telegram.WebApp.expand();
                }
            }
            
            function addToCart(name, price) {
                cart.push({ name: name, price: price });
                updateCart();
            }
            
            function updateCart() {
                const total = cart.reduce((sum, item) => sum + item.price, 0).toFixed(2);
                document.getElementById('cart-total').textContent = total + ' PLN';
                document.getElementById('cart-items').textContent = cart.length + ' produktów';
            }
            
            function checkout() {
                if (cart.length === 0) {
                    alert('Dodaj produkty do koszyka!');
                    return;
                }
                const total = cart.reduce((sum, item) => sum + item.price, 0).toFixed(2);
                const message = 'Zamowienie: ' + cart.map(item => item.name).join(', ') + ' - Suma: ' + total + ' PLN';
                if (window.Telegram && window.Telegram.WebApp) {
                    window.Telegram.WebApp.sendData(message);
                }
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
