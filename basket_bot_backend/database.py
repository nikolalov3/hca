from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Tworzymy plik bazy danych o nazwie hoop.db
DATABASE_URL = "sqlite+aiosqlite:///./hoop.db"

engine = create_async_engine(DATABASE_URL, echo=True)

# Fabryka sesji (połączeń)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Funkcja pomocnicza do pobierania bazy w endpointach
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
