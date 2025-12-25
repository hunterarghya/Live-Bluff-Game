from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from backend.db import users_col
from backend.auth import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=2)

@router.post("/register")
def register(payload: RegisterIn):
    if users_col.find_one({"email": payload.email}):
        raise HTTPException(400, "Email already registered")
    
    user = {
        "email": payload.email,
        "name": payload.name,
        "password": hash_password(payload.password),
        "created_at": datetime.utcnow()
    }
    res = users_col.insert_one(user)
    user_id = str(res.inserted_id)
    token = create_access_token({"sub": user_id, "email": payload.email, "name": payload.name})
    return {"access_token": token, "token_type": "bearer", "name": payload.name}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_col.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(401, "Invalid email or password")

    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name", "Player")
    })
    return {"access_token": token, "token_type": "bearer", "name": user.get("name")}