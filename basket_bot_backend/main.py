from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

# Importy z naszych nowych plików
from database import engine, Base, get_db
from models import User

app = FastAPI()

# Konfiguracja CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model danych przychodzących z frontendu
class UserProfileUpdate(BaseModel):
    telegram_id: int
    name: str | None = None
    age: str | None = None
    height: str | None = None
    number: str | None = None
    wallet_address: str | None = None

# Tworzenie tabel przy starcie
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- ENDPOINTY ---

@app.get("/")
async def root():
    return {"message": "HOOP.CONNECT Backend działa!"}

# Pobieranie profilu
@app.get("/api/profile/{telegram_id}")
async def get_profile(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return {"name": "", "age": "", "height": "", "number": ""}
    return user

# Zapisywanie profilu
@app.post("/api/profile")
async def update_profile(data: UserProfileUpdate, db: AsyncSession = Depends(get_db)):    result = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=data.telegram_id)
        db.add(user)
    
    if data.name is not None: user.name = data.name
    if data.age is not None: user.age = data.age
    if data.height is not None: user.height = data.height
    if data.number is not None: user.number = data.number
    if data.wallet_address is not None: user.wallet_address = data.wallet_address

    await db.commit()
    await db.refresh(user)
    return {"status": "success", "user": user}

@app.get("/api/matches")
async def get_matches():
    return [
        {
            "id": 1,
            "venue": "Arena Ursynów",
            "date": "Dziś, 18:00",
            "price": "15 PLN",
            "slots": "4/10",
            "status": "open"
        },
        {
            "id": 2,
            "venue": "OSiR Wola",
            "date": "Jutro, 20:00",
            "price": "20 PLN",
            "slots": "10/10",
            "status": "full"
        }
    ]
