import os
import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
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
        print("⚠️ BRAK TOKENU BOTA! Bot nie wystartuje.")
        return None
    print(f"🤖 Uruchamiam bota z WebApp URL: {WEBAPP_URL}")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    return application

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Baza danych podłączona.")
    bot_app = await start_bot()
    yield
    if bot_app:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
        print("🛑 Bot zatrzymany.")

app = FastAPI(lifespan=lifespan)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODEL DANYCH (ZMODYFIKOWANY - TOLERANCYJNY) ---
class UserProfileUpdate(BaseModel):
    # Przyjmujemy WSZYSTKO jako opcjonalne, zeby zobaczyc co przychodzi w logach
    telegram_id: int | str | None = None
    name: str | None = None
    age: str | int | None = None
    height: str | int | None = None
    number: str | int | None = None
    wallet_address: str | None = None

    class Config:
        extra = "allow"

# --- ENDPOINTY ---

@app.get("/")
async def root():
    return {"message": "HOOP.CONNECT działa na Railway 🚀"}

@app.get("/api/profile/{telegram_id}")
async def get_profile(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        return {"name": "", "age": "", "height": "", "number": ""}
    return user

@app.post("/api/profile")
async def update_profile( UserProfileUpdate, db: AsyncSession = Depends(get_db)):
    # LOGOWANIE DLA CELÓW DEBUGOWANIA
    print(f"DEBUG: Otrzymane dane JSON: {data.dict()}")

    if not data.telegram_id:
        print("BŁĄD: Brak telegram_id w requestcie!")
        return {"status": "error", "message": "Brak telegram_id"}

    try:
        tg_id = int(data.telegram_id)
    except ValueError:
        print(f"BŁĄD: telegram_id nie jest liczbą: {data.telegram_id}")
        return {"status": "error", "message": "telegram_id musi byc liczba"}

    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=tg_id)
        db.add(user)
    
    if data.name is not None: user.name = data.name
    # Konwersja na stringi (bo baza chce String, a frontend może przysłać int)
    if data.age is not None: user.age = str(data.age)
    if data.height is not None: user.height = str(data.height)
    if data.number is not None: user.number = str(data.number)
    if data.wallet_address is not None: user.wallet_address = data.wallet_address

    await db.commit()
    await db.refresh(user)
    print("SUKCES: Profil zaktualizowany!")
    return {"status": "success", "user": user}

@app.get("/api/matches")
async def get_matches():
    return [
        {"id": 1, "venue": "Arena Ursynów", "date": "Dziś, 18:00", "price": "15 PLN", "slots": "4/10", "status": "open"},
        {"id": 2, "venue": "OSiR Wola", "date": "Jutro, 20:00", "price": "20 PLN", "slots": "10/10", "status": "full"}
    ]
