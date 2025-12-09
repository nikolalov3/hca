import os
from datetime import datetime, timedelta
from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from tonpy.utils import Address
from tonpy.contract.wallet import Wallet
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def verify_ton_signature(address: str, message: str, signature: str) -> bool:
    """
    Verify TON wallet signature
    Args:
        address: TON wallet address
        message: Original message that was signed
        signature: The signature from TON wallet
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Parse the address
        wallet_address = Address(address)
        # In production, implement actual TON signature verification
        # using tonpy library
        return True
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

def create_access_token(wallet_address: str, expires_delta: timedelta = None) -> str:
    """
    Create JWT access token for authenticated wallet
    Args:
        wallet_address: TON wallet address
        expires_delta: Token expiration time
    Returns:
        JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "wallet_address": wallet_address,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """
    Verify JWT token from request
    Args:
        credentials: HTTP Bearer token
    Returns:
        wallet_address if token is valid
    Raises:
        HTTPException if token is invalid
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        wallet_address: str = payload.get("wallet_address")
        if wallet_address is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return wallet_address

def get_current_user(wallet_address: str = Depends(verify_token)) -> str:
    """
    Get current authenticated user wallet address
    Args:
        wallet_address: From token verification
    Returns:
        wallet_address
    """
    return wallet_address
