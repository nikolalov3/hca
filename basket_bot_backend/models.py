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
