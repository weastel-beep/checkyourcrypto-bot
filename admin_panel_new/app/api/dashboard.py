from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.models.admin import AdminUser
from app.models.user import User, Check, Payment
from app.schemas.dashboard import DashboardResponse, DashboardStats, ChartData
from app.api.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики для дашборда"""
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    
    # Статистика пользователей
    total_users = db.query(User).count()
    new_users_today = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()
    
    # Статистика проверок
    total_checks = db.query(Check).count()
    checks_today = db.query(Check).filter(
        func.date(Check.created_at) == today
    ).count()
    
    # Статистика платежей
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "completed"
    ).scalar() or 0
    
    revenue_today = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            func.date(Payment.created_at) == today
        )
    ).scalar() or 0
    
    revenue_week = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            Payment.created_at >= week_ago
        )
    ).scalar() or 0
    
    # Средний чек
    avg_check_amount = db.query(func.avg(Payment.amount)).filter(
        Payment.status == "completed"
    ).scalar() or 0
    
    return DashboardStats(
        total_users=total_users,
        new_users_today=new_users_today,
        total_checks=total_checks,
        checks_today=checks_today,
        total_revenue=total_revenue,
        revenue_today=revenue_today,
        revenue_week=revenue_week,
        avg_check_amount=avg_check_amount
    )

@router.get("/charts/user-activity", response_model=ChartData)
def get_user_activity_chart(
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """График активности пользователей за последние 7 дней"""
    labels = []
    data = []
    
    for i in range(7):
        date = datetime.utcnow().date() - timedelta(days=i)
        labels.insert(0, date.strftime("%d.%m"))
        
        count = db.query(User).filter(
            func.date(User.created_at) == date
        ).count()
        data.insert(0, count)
    
    return ChartData(labels=labels, data=data)

@router.get("/charts/blockchain", response_model=ChartData)
def get_blockchain_chart(
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """График активности по блокчейнам"""
    # Получаем топ-5 блокчейнов
    blockchain_stats = db.query(
        Check.chain,
        func.count(Check.id).label('count')
    ).group_by(Check.chain).order_by(
        func.count(Check.id).desc()
    ).limit(5).all()
    
    labels = [stat.chain for stat in blockchain_stats]
    data = [stat.count for stat in blockchain_stats]
    
    return ChartData(labels=labels, data=data)

@router.get("/charts/revenue", response_model=ChartData)
def get_revenue_chart(
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """График выручки за последние 7 дней"""
    labels = []
    data = []
    
    for i in range(7):
        date = datetime.utcnow().date() - timedelta(days=i)
        labels.insert(0, date.strftime("%d.%m"))
        
        revenue = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.status == "completed",
                func.date(Payment.created_at) == date
            )
        ).scalar() or 0
        data.insert(0, float(revenue))
    
    return ChartData(labels=labels, data=data)

@router.get("/recent-activity")
def get_recent_activity(
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Последняя активность"""
    # Последние пользователи
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
    
    # Последние платежи
    recent_payments = db.query(Payment).filter(
        Payment.status == "completed"
    ).order_by(Payment.created_at.desc()).limit(5).all()
    
    # Последние проверки
    recent_checks = db.query(Check).order_by(Check.created_at.desc()).limit(5).all()
    
    return {
        "recent_users": [
            {
                "id": user.tg_id,
                "username": user.username,
                "created_at": user.created_at,
                "type": "user"
            } for user in recent_users
        ],
        "recent_payments": [
            {
                "id": payment.id,
                "amount": float(payment.amount),
                "method": payment.method,
                "created_at": payment.created_at,
                "type": "payment"
            } for payment in recent_payments
        ],
        "recent_checks": [
            {
                "id": check.id,
                "chain": check.chain,
                "type": check.type,
                "created_at": check.created_at,
                "type": "check"
            } for check in recent_checks
        ]
    }
