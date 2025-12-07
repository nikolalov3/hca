import os
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import aiohttp
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("8353950120:AAExoG7jNlgLaM3ngovzCwVOyY8bLsG0deU")
WEBHOOK_URL = os.getenv("https://hca-production.up.railway.app")
WEBAPP_URL = os.getenv("https://hca-production.up.railway.app")

if not all([TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBAPP_URL]):
    raise ValueError("Missing required environment variables: TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBAPP_URL")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

class CourtStatus(str, Enum):
    AVAILABLE = "dostępna"
    BOOKED = "zarezerwowana"
    MAINTENANCE = "konserwacja"

class UserSession:
    def __init__(self):
        self.users: Dict[int, dict] = {}
    
    def get_user(self, user_id: int):
        if user_id not in self.users:
            self.users[user_id] = {
                "wallet_connected": False,
                "wallet_address": None,
                "reservations": [],
                "state": "main_menu"
            }
        return self.users[user_id]
    
    def update_user(self, user_id: int, **kwargs):
        user = self.get_user(user_id)
        user.update(kwargs)

sessions = UserSession()

# Mock database for courts
COURTS_DB = {
    "1": {
        "id": "1",
        "name": "Boisko 1",
        "status": CourtStatus.AVAILABLE,
        "price_per_hour": 50,
        "bookings": []
    },
    "2": {
        "id": "2",
        "name": "Boisko 2",
        "status": CourtStatus.AVAILABLE,
        "price_per_hour": 60,
        "bookings": []
    },
    "3": {
        "id": "3",
        "name": "Boisko 3",
        "status": CourtStatus.AVAILABLE,
        "price_per_hour": 55,
        "bookings": []
    }
}

async def send_telegram_message(chat_id: int, text: str, reply_markup: Optional[dict] = None):
    """Wyślij wiadomość Telegram"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        async with session.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload) as resp:
            if resp.status != 200:
                logger.error(f"Telegram API error: {await resp.text()}")
            return await resp.json()

async def set_webhook(webhook_url: str):
    """Ustaw webhook dla bota"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query", "web_app_info"]
        }
        async with session.post(f"{TELEGRAM_API_URL}/setWebhook", json=payload) as resp:
            result = await resp.json()
            logger.info(f"Webhook set result: {result}")
            return result

async def get_webhook_info():
    """Pobierz informacje o webhoku"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TELEGRAM_API_URL}/getWebhookInfo") as resp:
            return await resp.json()

def get_main_menu_keyboard():
    """Główne menu"""
    return {
        "inline_keyboard": [
            [{"text": "🔗 Połącz portfel", "callback_data": "connect_wallet"}],
            [{"text": "📅 Moje rezerwacje", "callback_data": "my_reservations"}],
            [{"text": "🏀 Dostępne boiska", "callback_data": "available_courts"}],
            [{"text": "💬 Wsparcie", "callback_data": "support"}]
        ]
    }

def get_courts_keyboard():
    """Keyboard z dostępnymi boiskami"""
    keyboard = []
    for court_id, court in COURTS_DB.items():
        status_emoji = "✅" if court["status"] == CourtStatus.AVAILABLE else "❌"
        keyboard.append([{
            "text": f"{status_emoji} {court['name']} ({court['price_per_hour']} PLN/h)",
            "callback_data": f"court_{court_id}"
        }])
    keyboard.append([{"text": "◀️ Wróć", "callback_data": "back_main"}])
    return {"inline_keyboard": keyboard}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup i shutdown events"""
    logger.info("Aplikacja startuje...")
    webhook_result = await set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook status: {webhook_result}")
    yield
    logger.info("Aplikacja się wyłącza...")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "webhook": WEBHOOK_URL,
        "webapp": WEBAPP_URL
    }

@app.post("/webhook")
async def webhook(request: Request):
    """Webhook dla aktualizacji Telegram"""
    try:
        data = await request.json()
        
        # Obsługa wiadomości
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            user_id = message["from"]["id"]
            text = message.get("text", "")
            
            sessions.update_user(user_id, state="main_menu")
            
            if text == "/start":
                await send_telegram_message(
                    chat_id,
                    "🏀 <b>Witaj w HOOP.CONNECT!</b>\n\nAplicacja do rezerwacji hal do gry w koszykówkę.\n\nPołącz swój portfel TON aby zarezerwować boisko.",
                    reply_markup=get_main_menu_keyboard()
                )
        
        # Obsługa callback queries
        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["from"]["id"]
            user_id = callback["from"]["id"]
            callback_data = callback["data"]
            message_id = callback["message"]["message_id"]
            
            if callback_data == "connect_wallet":
                user = sessions.get_user(user_id)
                if not user["wallet_connected"]:
                    await send_telegram_message(
                        chat_id,
                        "🔗 <b>Połącz portfel TON</b>\n\nUżyj aplikacji Tonkeeper aby połączyć swój portfel.\n\n<i>Wiadomość wysłana. Skanuj kod QR w Tonkeeper.</i>"
                    )
                    sessions.update_user(user_id, wallet_connected=True, wallet_address="EQxxx...")
                    
                    await send_telegram_message(
                        chat_id,
                        f"✅ Portfel połączony: EQxxx...\n\nMożesz teraz rezerwować boiska!",
                        reply_markup=get_main_menu_keyboard()
                    )
                else:
                    await send_telegram_message(
                        chat_id,
                        "✅ Twój portfel jest już połączony.",
                        reply_markup=get_main_menu_keyboard()
                    )
            
            elif callback_data == "available_courts":
                await send_telegram_message(
                    chat_id,
                    "🏀 <b>Dostępne boiska:</b>",
                    reply_markup=get_courts_keyboard()
                )
            
            elif callback_data.startswith("court_"):
                court_id = callback_data.split("_")[1]
                court = COURTS_DB.get(court_id)
                if court:
                    user = sessions.get_user(user_id)
                    if not user["wallet_connected"]:
                        await send_telegram_message(
                            chat_id,
                            "⚠️ Musisz najpierw połączyć portfel aby zarezerwować boisko.\n\nWróć do menu głównego i kliknij 'Połącz portfel'.",
                            reply_markup=get_main_menu_keyboard()
                        )
                    else:
                        await send_telegram_message(
                            chat_id,
                            f"📅 <b>{court['name']}</b>\n\nCena: {court['price_per_hour']} PLN/h\nStatus: {court['status']}\n\nOtwórz aplikację poniżej aby zarezerwować:",
                            reply_markup={
                                "inline_keyboard": [[{
                                    "text": "📱 Otwórz aplikację",
                                    "web_app": {"url": f"{WEBAPP_URL}?court={court_id}&user={user_id}"}
                                }]],
                                "inline_keyboard": [[{"text": "◀️ Wróć", "callback_data": "back_main"}]]
                            }
                        )
            
            elif callback_data == "my_reservations":
                user = sessions.get_user(user_id)
                if not user["reservations"]:
                    await send_telegram_message(
                        chat_id,
                        "📅 Brak rezerwacji.\n\nZarezerwuj boisko aby je zobaczyć tutaj.",
                        reply_markup=get_main_menu_keyboard()
                    )
                else:
                    res_text = "📅 <b>Twoje rezerwacje:</b>\n\n"
                    for res in user["reservations"]:
                        res_text += f"• {res['court']} - {res['date']} ({res['time']})\n"
                    await send_telegram_message(chat_id, res_text, reply_markup=get_main_menu_keyboard())
            
            elif callback_data == "support":
                await send_telegram_message(
                    chat_id,
                    "💬 <b>Wsparcie:</b>\n\nPróblemy? Skontaktuj się z nami:\nEmail: support@hoop.connect\nTelegram: @hoopconnect_support",
                    reply_markup=get_main_menu_keyboard()
                )
            
            elif callback_data == "back_main":
                await send_telegram_message(
                    chat_id,
                    "🏀 <b>HOOP.CONNECT</b>\n\nGłówne menu",
                    reply_markup=get_main_menu_keyboard()
                )
        
        return {"ok": True}
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}

@app.get("/reset-webhook")
async def reset_webhook():
    """Resetuj webhook (NIE używaj BotFather)"""
    try:
        result = await set_webhook(WEBHOOK_URL)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Reset webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Serve HTML z frontendem"""
    html_content = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HOOP.CONNECT - Rezerwacja hal do koszykówki</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary-light: #1a1a1a;
            --accent-light: #7CB342;
            --bg-light: #ffffff;
            --text-light: #333;
            --primary-dark: #ffffff;
            --accent-dark: #5DADE2;
            --bg-dark: #1a1a1a;
            --text-dark: #ffffff;
        }
        
        @media (prefers-color-scheme: dark) {
            body {
                background: var(--bg-dark);
                color: var(--text-dark);
            }
            .header {
                background: var(--primary-dark);
                color: var(--text-dark);
            }
            .btn-primary {
                background: var(--accent-dark);
                color: white;
            }
            .btn-primary:hover {
                background: #4A96C9;
            }
            .court-card {
                background: #2d2d2d;
                border: 1px solid var(--accent-dark);
            }
        }
        
        @media (prefers-color-scheme: light) {
            body {
                background: var(--bg-light);
                color: var(--text-light);
            }
            .header {
                background: var(--primary-light);
                color: white;
            }
            .btn-primary {
                background: var(--accent-light);
                color: white;
            }
            .btn-primary:hover {
                background: #689F38;
            }
            .court-card {
                background: #f5f5f5;
                border: 1px solid var(--accent-light);
            }
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            transition: background 0.3s, color 0.3s;
        }
        
        .header {
            padding: 20px;
            text-align: center;
            transition: background 0.3s;
        }
        
        .logo {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            letter-spacing: 2px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .section {
            margin: 30px 0;
        }
        
        .section-title {
            font-size: 20px;
            font-
