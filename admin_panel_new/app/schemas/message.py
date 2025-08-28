from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class MassMessageBase(BaseModel):
    title: str
    content: str
    language: str = "ru"
    user_filter: str = "all"
    min_balance: Optional[Decimal] = None
    max_balance: Optional[Decimal] = None
    user_language: Optional[str] = None
    is_active_only: bool = True
    scheduled_at: Optional[datetime] = None

class MassMessageCreate(MassMessageBase):
    pass

class MassMessageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    user_filter: Optional[str] = None
    min_balance: Optional[Decimal] = None
    max_balance: Optional[Decimal] = None
    user_language: Optional[str] = None
    is_active_only: Optional[bool] = None
    scheduled_at: Optional[datetime] = None

class MassMessageResponse(MassMessageBase):
    id: int
    status: str
    created_by_id: Optional[int] = None
    sent_at: Optional[datetime] = None
    total_users: int
    sent_count: int
    failed_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MassMessageListResponse(BaseModel):
    messages: List[MassMessageResponse]
    total: int
    page: int
    limit: int
    pages: int

class UserMessageBase(BaseModel):
    user_id: int
    message_type: str = "personal"
    subject: str
    content: str
    language: str = "ru"

class UserMessageCreate(UserMessageBase):
    pass

class UserMessageResponse(UserMessageBase):
    id: int
    sent_by_id: int
    status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    mass_message_id: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
