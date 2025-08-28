from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# Схемы для меню
class BotMenuItemBase(BaseModel):
    text: str
    callback_data: Optional[str] = None
    row_position: int
    column_position: int
    parent_item_id: Optional[int] = None
    is_active: bool = True

class BotMenuItemCreate(BotMenuItemBase):
    pass

class BotMenuItemUpdate(BaseModel):
    text: Optional[str] = None
    callback_data: Optional[str] = None
    row_position: Optional[int] = None
    column_position: Optional[int] = None
    parent_item_id: Optional[int] = None
    is_active: Optional[bool] = None

class BotMenuItemResponse(BotMenuItemBase):
    id: int
    menu_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    children: List['BotMenuItemResponse'] = []
    
    class Config:
        from_attributes = True

# Схемы для меню
class BotMenuBase(BaseModel):
    name: str
    language: str
    menu_type: str  # "reply_keyboard", "inline_keyboard"
    is_active: bool = True

class BotMenuCreate(BotMenuBase):
    items: List[BotMenuItemCreate] = []

class BotMenuUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    menu_type: Optional[str] = None
    is_active: Optional[bool] = None

class BotMenuResponse(BotMenuBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[BotMenuItemResponse] = []
    
    class Config:
        from_attributes = True

class BotMenuListResponse(BaseModel):
    menus: List[BotMenuResponse]
    total: int
    page: int
    limit: int
    pages: int

# Схемы для управления меню
class MenuStructureRequest(BaseModel):
    """Запрос на создание структуры меню"""
    menu_name: str
    language: str
    menu_type: str
    structure: List[List[Dict[str, str]]]  # [[{"text": "🔍 Проверка", "callback": "check"}], [{"text": "💰 Пополнить"}]]

class MenuImportRequest(BaseModel):
    """Запрос на импорт меню"""
    menus: Dict[str, Dict[str, List[List[Dict[str, str]]]]]  # menu_name -> {language -> structure}

# Обновляем схему текстов для связи с меню
class BotTextUpdate(BaseModel):
    content: Optional[str] = None
    is_active: Optional[bool] = None
    version: Optional[int] = None
    menu_item_id: Optional[int] = None  # связь с кнопкой меню
