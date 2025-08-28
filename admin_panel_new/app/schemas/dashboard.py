from pydantic import BaseModel
from typing import List, Dict, Any

class ChartData(BaseModel):
    labels: List[str]
    data: List[float]

class DashboardStats(BaseModel):
    total_users: int
    total_checks: int
    total_payments: int
    total_revenue: float
    checks_today: int
    revenue_today: float
    avg_check_amount: float

class DashboardResponse(BaseModel):
    stats: DashboardStats
    user_activity_chart: ChartData
    revenue_chart: ChartData
    recent_activity: List[Dict[str, Any]]
