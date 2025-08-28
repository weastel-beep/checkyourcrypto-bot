from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class BotTextBase(BaseModel):
    category: str
    language: str
    content: str
    is_active: bool = True
    version: int = 1

class BotTextCreate(BotTextBase):
    pass

class BotTextUpdate(BaseModel):
    content: Optional[str] = None
    is_active: Optional[bool] = None
    version: Optional[int] = None

class BotTextResponse(BotTextBase):
    id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BotTextListResponse(BaseModel):
    texts: List[BotTextResponse]
    total: int
    page: int
    limit: int
    pages: int

class TextCategoryResponse(BaseModel):
    category: str
    languages: List[str]
    texts: Dict[str, str]  # language -> content

class TextImportRequest(BaseModel):
    texts: Dict[str, Dict[str, str]]  # category -> {language -> content}

class TextSyncRequest(BaseModel):
    category: Optional[str] = None
    language: Optional[str] = None
