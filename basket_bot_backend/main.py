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
    if not TOKEN: return None
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    return application

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    bot_app = await start_bot()
    yield
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

@app.get("/")
async def root():
    return {"message": "HOOP.CONNECT Backend"}

@app.get("/api/profile/{telegram_id}")
async def get_profile(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user: return {"name": "", "age": "", "height": "", "number": ""}
    return user

# --- TUTAJ JEST KLUCZOWA ZMIANA ---
# Nie używamy UserProfileUpdate. Używamy surowego Request.
# To eliminuje błąd 422.

@app.post("/api/profile")
async def update_profile(request: Request, db: AsyncSession = Depends(get_db)):
    # 1. Odczytujemy surowy tekst
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        print(f"🛑 DEBUG RAW BODY: {body_str}")  # <--- SZUKAJ TEGO W LOGACH!
        
        data = json.loads(body_str)
    except Exception as e:
        print(f"Błąd parsowania JSON: {e}")
        return {"status": "error", "message": "To nie jest JSON"}

    # 2. Wyciągamy dane ręcznie
    # Używamy .get() żeby nie wywaliło błędu jak czegoś brakuje
    raw_id = data.get("telegram_id")
    
    if raw_id is None:
        print("BŁĄD: Brak telegram_id w danych!")
        return {"status": "error", "message": "Brak ID"}

    try:
        tg_id = int(raw_id)
    except:
        print(f"BŁĄD: ID to nie liczba: {raw_id}")
        return {"status": "error", "message": "ID musi byc liczba"}

    # 3. Zapis do bazy
    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=tg_id)
        db.add(user)
    
    # Bezpieczne przypisanie (rzutowanie na stringi dla pewności)
    if "name" in  user.name = str(data["name"]) if data["name"] else ""
    if "age" in  user.age = str(data["age"]) if data["age"] else ""
    if "height" in  user.height = str(data["height"]) if data["height"] else ""
    if "number" in  user.number = str(data["number"]) if data["number"] else ""
    if "wallet_address" in  user.wallet_address = str(data["wallet_address"]) if data["wallet_address"] else ""

    await db.commit()
    await db.refresh(user)
    print("✅ SUKCES: Zapisano dane!")
    return {"status": "success", "user": user}

@app.get("/api/matches")
async def get_matches():
    return [
        {"id": 1, "venue": "Arena Ursynów", "date": "Dziś, 18:00", "price": "15 PLN", "slots": "4/10", "status": "open"},
        {"id": 2, "venue": "OSiR Wola", "date": "Jutro, 20:00", "price": "20 PLN", "slots": "10/10", "status": "full"}
    ]
