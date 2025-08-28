from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, Text, ForeignKey, JSON
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class AdminUser(Base):
    """Модель администратора"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=True)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(20), default="moderator")  # superadmin, admin, moderator
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32), nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    created_messages = relationship("MassMessage", back_populates="created_by")
    sent_user_messages = relationship("UserMessage", back_populates="sent_by")
    created_texts = relationship("BotText", back_populates="created_by")

class MassMessage(Base):
    """Массовые сообщения"""
    __tablename__ = "mass_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="ru")
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    status = Column(String(20), default="DRAFT")  # DRAFT, SCHEDULED, SENDING, COMPLETED, CANCELLED, FAILED
    user_filter = Column(String(20), default="all")
    min_balance = Column(Numeric(10, 2), nullable=True)
    max_balance = Column(Numeric(10, 2), nullable=True)
    user_language = Column(String(10), nullable=True)
    is_active_only = Column(Boolean, default=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    total_users = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    created_by = relationship("AdminUser", back_populates="created_messages")
    user_messages = relationship("UserMessage", back_populates="mass_message")

class BotText(Base):
    """Тексты бота для разных языков"""
    __tablename__ = "bot_texts"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # welcome, main_menu, check, etc.
    language = Column(String(10), nullable=False)  # ru, en, es, fr, de
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    created_by = relationship("AdminUser", back_populates="created_texts")

class UserMessage(Base):
    """Персональные сообщения пользователям"""
    __tablename__ = "user_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    message_type = Column(String(20), default="personal")  # personal, mass, system, support
    subject = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="ru")
    sent_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, delivered, read, failed
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    mass_message_id = Column(Integer, ForeignKey("mass_messages.id"), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    sent_by = relationship("AdminUser", back_populates="sent_user_messages")
    mass_message = relationship("MassMessage", back_populates="user_messages")
