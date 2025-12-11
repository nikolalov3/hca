from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    wallet_address = Column(String, primary_key=True, index=True, unique=True)
    username = Column(String, nullable=True)

    # Pola profilu
    name = Column(String, default="")
    age = Column(String, default="")
    height = Column(String, default="")
    number = Column(String, default="")

    # Timestamp'y
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    matches_created = relationship("Match", back_populates="organizer")
    matches_joined = relationship("MatchParticipant", back_populates="user")
        profile = relationship("Profile", back_populates="user", uselist=False)


class Match(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organizer_wallet = Column(String, ForeignKey("users.wallet_address"), nullable=False)
    venue = Column(String, nullable=False)  # Nazwa miejsca
    crowdfund_amount = Column(Integer, default=0)  # Kwota zrzutki (PLN)
    slots_needed = Column(Integer, nullable=False)  # 8 (4v4) lub 10 (5v5)
    current_players = Column(Integer, default=1)  # Liczba obecnych graczy

    # Timestamp'y
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    organizer = relationship("User", back_populates="matches_created")
    participants = relationship("MatchParticipant", back_populates="match", cascade="all, delete-orphan")


class MatchParticipant(Base):
    __tablename__ = "match_participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.match_id"), nullable=False, index=True)
    user_wallet = Column(String, ForeignKey("users.wallet_address"), nullable=False, index=True)

    # Timestamp
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    match = relationship("Match", back_populates="participants")
    user = relationship("User", back_populates="matches_joined")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.wallet_address"), nullable=False, unique=True, index=True)    
    # Dane profilu
    nickname = Column(String, nullable=True)  # Nick gracza
    age = Column(Integer, nullable=True)  # Wiek
    city = Column(String, nullable=True)  # Miasto
    skill_level = Column(String, nullable=True)  # Poziom umiejętności (beginner, intermediate, advanced)
    preferred_position = Column(String, nullable=True)  # Preferowana pozycja (G, F, C)
    bio = Column(String, nullable=True)  # Opis/biografia
    phone = Column(String, nullable=True)  # Numer telefonu
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="profile")
