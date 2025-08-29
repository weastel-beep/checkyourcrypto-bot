"""
Единые схемы Pydantic для объединенного API
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class TextBase(BaseModel):
    category: str
    language: str = "ru"
    content: str
    version: int = 1
    is_active: bool = True


class TextCreate(TextBase):
    pass


class TextUpdate(BaseModel):
    content: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None


class TextResponse(TextBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = False
    stages: Optional[List[Dict[str, Any]]] = None


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    stages: Optional[List[Dict[str, Any]]] = None


class ScenarioResponse(ScenarioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class SettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


class SettingResponse(SettingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
