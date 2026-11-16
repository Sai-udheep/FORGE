from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class StreakMetrics(BaseModel):
    current_streak_days: int
    best_streak_days: int
    is_streak_active_today: bool

class DayVelocity(BaseModel):
    date: str
    planned_minutes: int
    actual_minutes: int
    tasks_completed: int

class DashboardAnalyticsResponse(BaseModel):
    today_date: str
    today_tasks_total: int
    today_tasks_completed: int
    today_completion_percentage: float
    today_focus_minutes: int
    streak: StreakMetrics
    goals_progress: List[Dict[str, Any]]
    upcoming_reminders_count: int
    weekly_velocity: List[DayVelocity]
