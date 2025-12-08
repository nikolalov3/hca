import os
import asyncio
import json
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Importy lokalne
from database import engine, Base, get_db
from models import User

# --- KONFIGURACJA BOTA ---
TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://hca-production.up.railway.app")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🏀 GRAJ W KOSZA", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        "Siemano! Gotowy na mecz? Kliknij poniżej (Cloud ☁️):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_bot():
    if not TOKEN:
        print("⚠️ BRAK TOKENU BOTA!")
        return None
    
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start_command))
    
    await app_bot.initialize()
    await app_bot.start()
    await app_bot.updater.start_polling()
    print("✅ Bot wystartował!")
    return app_bot

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Bazy
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start Bota
    bot_app = await start_bot()
    
    yield
    
    # Stop Bota
    if bot_app:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINTY ---

@app.post("/api/profile")
async def update_profile(request: Request, db: AsyncSession = Depends(get_db)):
    # 1. Odczytujemy dane
    try:
        data = await request.json()
        print(f"DEBUG: {data}")
    except Exception as e:
        print(f"Błąd JSON: {e}")
        return {"status": "error", "message": "Błąd JSON"}

    # 2. Wyciągamy ID
    raw_id = data.get("telegram_id")
    if not raw_id:
        return {"status": "error", "message": "Brak ID"}

    try:
        tg_id = int(raw_id)
    except:
        return {"status": "error", "message": "ID musi być liczbą"}

    # 3. Zapis do bazy
    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=tg_id)
        db.add(user)
    
    # 4. Aktualizacja pól (Metoda .get() jest bezpieczniejsza i krótsza)
    # Pobieramy wartość z JSONa, a jak jej nie ma, zostawiamy starą wartość (user.name)
    user.name = str(data.get("name") or user.name or "")
    user.age = str(data.get("age") or user.age or "")
    user.height = str(data.get("height") or user.height or "")
    user.number = str(data.get("number") or user.number or "")
    user.wallet_address = str(data.get("wallet_address") or user.wallet_address or "")

    await db.commit()
    await db.refresh(user)
    return {"status": "success", "user": user}


@app.get("/api/matches")
async def get_matches():
    return [
        {"id": 1, "venue": "Arena Ursynów", "date": "Dziś, 18:00", "price": "15 PLN", "slots": "4/10", "status": "open"},
            {"id": 2, "venue": "OSiR Wola", "date": "Jutro, 20:00", "price": "20 PLN", "slots": "10/10", "status": "full"},
            ]
@app.get("/api/profile/{telegram_id}")
async def get_profile(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        return {"status": "not_found", "message": "Użytkownik nie znaleziony"}
    return {
        "telegram_id": user.telegram_id,
        "name": user.name or "",
        "age": user.age or "",
        "height": user.height or "",
        "number": user.number or "",
        "wallet_address": user.wallet_address or ""
    }
    ]
