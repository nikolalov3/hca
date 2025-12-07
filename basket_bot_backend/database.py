import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Pobieramy adres bazy z ustawień Railway (zmienna środowiskowa)
# Jeśli jej nie ma (np. testujesz lokalnie), używamy SQLite jako awarii
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./hoop.db")

# Railway daje adres zaczynający się od "postgres://", ale SQLAlchemy woli "postgresql://"
# To mała poprawka, która to naprawia:
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# 2. Konfiguracja silnika
engine = create_async_engine(DATABASE_URL, echo=True)

# 3. Fabryka sesji
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# 4. Funkcja dla endpointów
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
