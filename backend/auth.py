from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

PWDCTX = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

SECRET_KEY = os.getenv("JWT_SECRET", "dev_secret_key_123")
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 1440  # 24 hours


def hash_password(password: str) -> str:
    return PWDCTX.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return PWDCTX.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
