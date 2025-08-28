"""
Модели данных для Check Your Crypto
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger, String, DateTime, Numeric, Boolean, 
    ForeignKey, JSON, Enum as SQLEnum, Text as SQLText, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class CheckType(str, Enum):
    """Тип проверки"""
    FREE = "free"
    PAID = "paid"


class PaymentStatus(str, Enum):
    """Статус платежа"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutboxStatus(str, Enum):
    """Статус исходящего сообщения"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    language: Mapped[str] = mapped_column(String(10), default="ru")
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    last_free_check: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    referral_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    checks = relationship("Check", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    referrals_given = relationship("Referral", foreign_keys="Referral.user_id", back_populates="user")
    referrals_received = relationship("Referral", foreign_keys="Referral.invited_id", back_populates="invited_user")
    outbox_messages = relationship("Outbox", back_populates="user")


class Check(Base):
    """Модель проверки адреса"""
    __tablename__ = "checks"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    chain: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[CheckType] = mapped_column(SQLEnum(CheckType), nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="checks")


class Payment(Base):
    """Модель платежа"""
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    tx_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payments")


class Setting(Base):
    """Модель настроек"""
    __tablename__ = "settings"
    
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(SQLText, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Text(Base):
    """Модель текстов (мультиязычность)"""
    __tablename__ = "texts"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lang: Mapped[str] = mapped_column(String(10), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(SQLText, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaymentMethod(Base):
    """Модель способов оплаты"""
    __tablename__ = "payment_methods"
    
    name: Mapped[str] = mapped_column(String(100), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Referral(Base):
    """Модель рефералов"""
    __tablename__ = "referrals"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    invited_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    reward_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "check", "balance"
    reward_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="referrals_given")
    invited_user = relationship("User", foreign_keys=[invited_id], back_populates="referrals_received")


class Outbox(Base):
    """Модель исходящих сообщений"""
    __tablename__ = "outbox"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)  # Telegram message payload
    status: Mapped[OutboxStatus] = mapped_column(SQLEnum(OutboxStatus), default=OutboxStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="outbox_messages")
