from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class UserBase(BaseModel):
    tg_id: int
    username: Optional[str] = None
    language: str = "ru"
    balance: Decimal = Decimal('0.00')
    is_blocked: bool = False

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    language: Optional[str] = None
    balance: Optional[Decimal] = None
    is_blocked: Optional[bool] = None

class UserResponse(UserBase):
    last_free_check: Optional[datetime] = None
    referral_code: Optional[str] = None
    referrer_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    limit: int
    pages: int

class UserBalanceUpdate(BaseModel):
    balance: Decimal

class UserMessageCreate(BaseModel):
    subject: str
    content: str
    language: str = "ru"
