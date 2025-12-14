import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Pobieramy adres
raw_url = os.getenv("DATABASE_URL")

# 2. Naprawiamy protokół dla asyncpg
# Railway daje: postgres://...
# SQLAlchemy chce: postgresql+asyncpg://...
if raw_url:
    if raw_url.startswith("postgres://"):
        DATABASE_URL = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif raw_url.startswith("postgresql://") and "asyncpg" not in raw_url:
         DATABASE_URL = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        DATABASE_URL = raw_url
else:
    # Fallback tylko dla lokalnych testów
    DATABASE_URL = "sqlite+aiosqlite:///./hoop.db"

print(f"DEBUG: Łączę z bazą: {DATABASE_URL.split('@')[0]}...") # Loguje początek adresu dla pewności

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
