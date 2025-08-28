from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, Text, ForeignKey, JSON
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"
    
    tg_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(100), nullable=True)
    language = Column(String(10), default="ru")
    balance = Column(Numeric(10, 2), default=0.00)
    is_blocked = Column(Boolean, default=False)
    last_free_check = Column(DateTime(timezone=True), nullable=True)
    referral_code = Column(String(20), unique=True, nullable=True)
    referrer_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    checks = relationship("Check", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class Check(Base):
    """Проверка адреса"""
    __tablename__ = "checks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    address = Column(String(255), nullable=False)
    chain = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)  # free, paid
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    user = relationship("User", back_populates="checks")

class Payment(Base):
    """Платеж"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(String(20), nullable=False)  # binance, crypto, card
    tx_id = Column(String(255), nullable=True)
    status = Column(String(20), default="pending")  # pending, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    user = relationship("User", back_populates="payments")
