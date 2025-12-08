from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True)
    wallet_address = Column(String, nullable=True)
    
    # Pola profilu
    name = Column(String, default="")
    age = Column(String, default="")
    height = Column(String, default="")
    number = Column(String, default="")

    class Match(Base):
            __tablename__ = "matches"
    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    venue = Column(String, nullable=False)  # Nazwa miejsca
    crowdfund_amount = Column(Integer, default=0)  # Kwota zrzutki (PLN)
    slots_needed = Column(Integer, nullable=False)  # 8 (4v4) lub 10 (5v5)
    current_players = Column(Integer, default=1)  # Liczba obecnych graczy
    organizer_id = Column(Integer, nullable=False)  # Telegram ID organizatora
