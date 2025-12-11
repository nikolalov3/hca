import os
import asyncio
import json
from pydantic import BaseModel
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from contextlib import asynccontextmanager
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Importy lokalne
from database import engine, Base, get_db
from models import User, Match, Profile
from auth import create_access_token, verify_token, get_current_user

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
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_id INTEGER"))    
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
    
    # 4. Aktualizacja pól
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

# --- MATCH ENDPOINTS ---

@app.post("/api/matches")
async def create_match(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
    except:
        return {"status": "error", "message": "Błąd JSON"}
    
    tg_id = data.get("telegram_id")
    venue = data.get("venue")
    crowdfund_amount = data.get("crowdfund_amount", 0)
    slots_needed = data.get("slots_needed")
    
    if not tg_id or not venue or not slots_needed:
        return {"status": "error", "message": "Brak wymaganych pól: telegram_id, venue, slots_needed"}
    
    if slots_needed not in [8, 10]:
        return {"status": "error", "message": "slots_needed musi być 8 (4v4) lub 10 (5v5)"}
    
    new_match = Match(
        venue=venue,
        crowdfund_amount=int(crowdfund_amount),
        slots_needed=int(slots_needed),
        current_players=1,
        organizer_id=int(tg_id)
    )
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)
    
    return {
        "status": "success",
        "match_id": new_match.match_id,
        "venue": new_match.venue,
        "crowdfund_amount": new_match.crowdfund_amount,
        "slots_needed": new_match.slots_needed,
        "current_players": new_match.current_players
    }

@app.get("/api/matches-list")
async def get_all_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match))
    matches = result.scalars().all()
    
    return [
        {
            "match_id": m.match_id,
            "venue": m.venue,
            "crowdfund_amount": m.crowdfund_amount,
            "slots_needed": m.slots_needed,
            "current_players": m.current_players,
            "slots_available": m.slots_needed - m.current_players,
            "organizer_id": m.organizer_id
        }
        for m in matches
    ]

@app.post("/api/matches/{match_id}/join")
async def join_match(match_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        tg_id = data.get("telegram_id")
    except:
        return {"status": "error", "message": "Błąd JSON lub brak telegram_id"}
    
    result = await db.execute(select(Match).where(Match.match_id == match_id))
    match = result.scalar_one_or_none()
    
    if not match:
        return {"status": "error", "message": "Mecz nie istnieje"}
    
    if match.current_players >= match.slots_needed:
        return {"status": "error", "message": "Mecz pełny!"}
    
    match.current_players += 1
    await db.commit()
    await db.refresh(match)
    
    return {
        "status": "success",
        "message": f"Dołączyłeś się do meczu! ({match.current_players}/{match.slots_needed})",
        "current_players": match.current_players,
        "slots_available": match.slots_needed - match.current_players
    }

# --- AUTH ENDPOINTS ---

class LoginRequest(BaseModel):
    wallet_address: str
    message: str
    signature: str

@app.post("/api/auth/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    TON Wallet authentication endpoint
    Verifies wallet signature and returns JWT token
    """
    try:
        # Verify the signature (simplified - implement full verification in production)
        wallet_address = request.wallet_address
        
        # Check if user exists or create new one
        result = await db.execute(select(User).where(User.wallet_address == wallet_address))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user with wallet address
            user = User(
                wallet_address=wallet_address,
                username="",
                telegram_id=None
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Generate JWT token
        access_token = create_access_token(wallet_address=wallet_address)
        
        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
            "wallet_address": wallet_address
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/auth/me")
async def get_profile(wallet_address: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Get current user profile
    Requires valid JWT token
    """
    try:
        result = await db.execute(select(User).where(User.wallet_address == wallet_address))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"status": "error", "message": "User not found"}
        
        return {
            "status": "success",
            "user": {
                "wallet_address": user.wallet_address,
                "username": user.username or "",
                "telegram_id": user.telegram_id or ""
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


                    
# ===== PROFILE ENDPOINTS =====

class ProfileUpdate(BaseModel):
    nickname: str | None = None
    age: int | None = None
    city: str | None = None
    skill_level: str | None = None  # beginner, intermediate, advanced
    preferred_position: str | None = None  # G, F, C
    bio: str | None = None
    phone: str | None = None


@app.get("/api/profile/me")
async def get_profile(wallet_address: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Get current user's profile
    Requires valid JWT token
    """
    try:
        # Get user with profile
        result = await db.execute(select(User).where(User.wallet_address == wallet_address))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"status": "error", "message": "User not found"}
        
        profile = user.profile
        
        if not profile:
            return {"status": "success", "profile": None}
        
        return {
            "status": "success",
            "profile": {
                "id": profile.id,
                "nickname": profile.nickname,
                "age": profile.age,
                "city": profile.city,
                "skill_level": profile.skill_level,
                "preferred_position": profile.preferred_position,
                "bio": profile.bio,
                "phone": profile.phone,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/profile/me")
async def 352
(profile_data: ProfileUpdate, wallet_address: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Create or update user's profile
    Requires valid JWT token
    """
    try:
        # Get user
        result = await db.execute(select(User).where(User.wallet_address == wallet_address))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"status": "error", "message": "User not found"}
        
        # Check if profile exists
        if user.profile:
            # Update existing profile
            profile = user.profile
            if profile_data.nickname is not None:
                profile.nickname = profile_data.nickname
            if profile_data.age is not None:
                profile.age = profile_data.age
            if profile_data.city is not None:
                profile.city = profile_data.city
            if profile_data.skill_level is not None:
                profile.skill_level = profile_data.skill_level
            if profile_data.preferred_position is not None:
                profile.preferred_position = profile_data.preferred_position
            if profile_data.bio is not None:
                profile.bio = profile_data.bio
            if profile_data.phone is not None:
                profile.phone = profile_data.phone
        else:
            # Create new profile
            profile = Profile(
                user_id=user.wallet_address,
                nickname=profile_data.nickname,
                age=profile_data.age,
                city=profile_data.city,
                skill_level=profile_data.skill_level,
                preferred_position=profile_data.preferred_position,
                bio=profile_data.bio,
                phone=profile_data.phone
            )
            db.add(profile)
        
        await db.commit()
        await db.refresh(profile)
        
        return {
            "status": "success",
            "message": "Profile saved successfully",
            "profile": {
                "id": profile.id,
                "nickname": profile.nickname,
                "age": profile.age,
                "city": profile.city,
                "skill_level": profile.skill_level,
                "preferred_position": profile.preferred_position,
                "bio": profile.bio,
                "phone": profile.phone,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }
        }
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": str(e)}
