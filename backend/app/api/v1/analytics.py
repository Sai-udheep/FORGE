from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.models.goal import Goal
from app.models.focus_session import FocusSession
from app.models.reminder import Reminder
from app.schemas.analytics import DashboardAnalyticsResponse, StreakMetrics, DayVelocity

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
def get_dashboard_analytics(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    
    # Today's tasks
    today_tasks = db.query(Task).filter(Task.scheduled_date == today).all()
    today_total = len(today_tasks)
    today_completed = sum(1 for t in today_tasks if t.status == "completed")
    today_pct = round((today_completed / today_total * 100), 1) if today_total > 0 else 0.0

    # Today's focus minutes
    sessions_today = db.query(FocusSession).filter(
        FocusSession.start_time >= datetime.combine(today, datetime.min.time())
    ).all()
    today_focus_mins = sum(s.actual_duration_minutes for s in sessions_today)

    # Streak calculation: count consecutive previous days with completed tasks
    current_streak = 0
    test_date = today
    # Check if active today
    has_activity_today = today_completed > 0 or today_focus_mins >= 15
    if has_activity_today:
        current_streak += 1
        test_date = today - timedelta(days=1)
    else:
        test_date = today - timedelta(days=1)

    while True:
        d_tasks = db.query(Task).filter(Task.scheduled_date == test_date, Task.status == "completed").count()
        d_sessions = db.query(FocusSession).filter(
            FocusSession.start_time >= datetime.combine(test_date, datetime.min.time()),
            FocusSession.start_time <= datetime.combine(test_date, datetime.max.time())
        ).count()
        if d_tasks > 0 or d_sessions > 0:
            current_streak += 1
            test_date -= timedelta(days=1)
        else:
            break

    # Goals summary
    goals = db.query(Goal).filter(Goal.status == "active").all()
    goals_progress = []
    for g in goals:
        g_tasks = db.query(Task).filter(Task.goal_id == g.id).all()
        g_total = len(g_tasks)
        g_done = sum(1 for t in g_tasks if t.status == "completed")
        pct = round((g_done / g_total * 100), 1) if g_total > 0 else 0.0
        goals_progress.append({
            "goal_id": g.id,
            "title": g.title,
            "priority": g.priority,
            "tasks_total": g_total,
            "tasks_completed": g_done,
            "progress_percentage": pct
        })

    # Upcoming reminders
    now = datetime.now(timezone.utc)
    reminders_count = db.query(Reminder).filter(
        Reminder.status == "scheduled",
        Reminder.reminder_time >= now
    ).count()

    # 7-day velocity
    weekly_velocity: List[DayVelocity] = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        d_tasks_all = db.query(Task).filter(Task.scheduled_date == day).all()
        d_done_count = sum(1 for t in d_tasks_all if t.status == "completed")
        planned_mins = sum(t.estimated_duration_minutes for t in d_tasks_all)
        actual_mins = sum(t.actual_duration_minutes for t in d_tasks_all)
        weekly_velocity.append(DayVelocity(
            date=day.isoformat(),
            planned_minutes=planned_mins,
            actual_minutes=actual_mins,
            tasks_completed=d_done_count
        ))

    return DashboardAnalyticsResponse(
        today_date=today.isoformat(),
        today_tasks_total=today_total,
        today_tasks_completed=today_completed,
        today_completion_percentage=today_pct,
        today_focus_minutes=today_focus_mins,
        streak=StreakMetrics(
            current_streak_days=current_streak,
            best_streak_days=max(current_streak, 7), # Initial anchor
            is_streak_active_today=has_activity_today
        ),
        goals_progress=goals_progress,
        upcoming_reminders_count=reminders_count,
        weekly_velocity=weekly_velocity
    )
