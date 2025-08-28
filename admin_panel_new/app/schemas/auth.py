from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserResponse(BaseModel):
    username: str
    role: str

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str = "moderator"

    class Config:
        from_attributes = True
