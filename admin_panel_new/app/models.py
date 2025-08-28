"""
Модели для Admin API - импортируем из бота
"""
import sys
import os

# Добавляем путь к модулю common
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, BigInteger, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    tg_id = Column(BigInteger, primary_key=True)
    username = Column(String(100), nullable=True)
    language = Column(String(10), default="ru")
    balance = Column(Numeric(10, 2), default=0.0)
    is_blocked = Column(Boolean, default=False)
    last_free_check = Column(DateTime, nullable=True)
    referral_code = Column(String(20), nullable=True)
    referrer_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Check(Base):
    __tablename__ = "checks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"))
    address = Column(String(255))
    chain = Column(String(50))
    type = Column(String(4))  # 'free' or 'paid'
    result = Column(Text)  # JSON as text
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="checks")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"))
    amount = Column(Numeric(10, 2))
    method = Column(String(50))
    tx_id = Column(String(255), nullable=True)
    status = Column(String(9))  # 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="payments")

class Text(Base):
    __tablename__ = "texts"
    
    id = Column(Integer, primary_key=True, index=True)
    lang = Column(String(10))
    key = Column(String(255))
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MassMessage(Base):
    __tablename__ = "mass_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    language = Column(String(10))
    status = Column(String(9))  # DRAFT, SCHEDULED, SENDING, COMPLETED, CANCELLED, FAILED
    min_balance = Column(Numeric(10, 2), nullable=True)
    max_balance = Column(Numeric(10, 2), nullable=True)
    user_language = Column(String(10), nullable=True)
    is_active_only = Column(Boolean, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    total_users = Column(Integer, nullable=True)
    sent_count = Column(Integer, nullable=True)
    failed_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MassMessageRecipient(Base):
    __tablename__ = "mass_message_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("mass_messages.id"))
    user_id = Column(BigInteger, ForeignKey("users.tg_id"))
    status = Column(String(20), default="PENDING")  # PENDING, SENT, DELIVERED, READ, FAILED
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    message = relationship("MassMessage")
    user = relationship("User")

# Добавляем отношения
User.checks = relationship("Check", back_populates="user")
User.payments = relationship("Payment", back_populates="user")

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class BotMenu(Base):
    """Модель для хранения меню бота"""
    __tablename__ = 'bot_menus'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # "main_menu", "settings_menu", etc.
    language = Column(String(10), nullable=False)  # "ru", "en"
    menu_type = Column(String(20), nullable=False)  # "reply_keyboard", "inline_keyboard"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с элементами меню
    items = relationship("BotMenuItem", back_populates="menu", cascade="all, delete-orphan")

class BotMenuItem(Base):
    """Модель для хранения элементов меню"""
    __tablename__ = 'bot_menu_items'
    
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey('bot_menus.id'), nullable=False)
    text = Column(String(100), nullable=False)  # "🔍 Проверка"
    callback_data = Column(String(100))  # "check_address" (для inline кнопок)
    row_position = Column(Integer, nullable=False)  # в какой строке кнопка
    column_position = Column(Integer, nullable=False)  # в каком столбце кнопка
    parent_item_id = Column(Integer, ForeignKey('bot_menu_items.id'))  # для подменю
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    menu = relationship("BotMenu", back_populates="items")
    parent = relationship("BotMenuItem", remote_side=[id])
    children = relationship("BotMenuItem")

class BotText(Base):
    """Модель для хранения текстов бота (обновленная)"""
    __tablename__ = 'bot_texts'
    
    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False)
    language = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    menu_item_id = Column(Integer, ForeignKey('bot_menu_items.id'))  # связь с кнопкой меню
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с элементом меню
    menu_item = relationship("BotMenuItem")
