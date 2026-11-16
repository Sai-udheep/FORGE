from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.models.focus_session import FocusSession
from app.api.v1.tasks import format_task_response

router = APIRouter(prefix="/planner", tags=["Planner"])

@router.get("/today")
def get_today_planner(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    
    # Scheduled for today
    today_tasks = db.query(Task).filter(Task.scheduled_date == today).order_by(Task.scheduled_time.asc()).all()
    # Overdue tasks (scheduled before today and still pending)
    overdue_tasks = db.query(Task).filter(
        Task.scheduled_date < today,
        Task.status.in_(["pending", "in_progress"])
    ).all()
    
    completed_today = sum(1 for t in today_tasks if t.status == "completed")
    total_today = len(today_tasks)
    percentage = round((completed_today / total_today * 100), 1) if total_today > 0 else 0.0

    active_focus = db.query(FocusSession).filter(FocusSession.status == "active").first()

    return {
        "date": today.isoformat(),
        "today_tasks": [format_task_response(t) for t in today_tasks],
        "overdue_tasks": [format_task_response(t) for t in overdue_tasks],
        "metrics": {
            "total_tasks": total_today,
            "completed_tasks": completed_today,
            "completion_percentage": percentage,
            "overdue_count": len(overdue_tasks)
        },
        "active_focus_session": {
            "id": active_focus.id,
            "task_id": active_focus.task_id,
            "session_type": active_focus.session_type,
            "start_time": active_focus.start_time.isoformat(),
            "planned_duration_minutes": active_focus.planned_duration_minutes
        } if active_focus else None
    }

@router.get("/week")
def get_week_planner(start_date: date = None, db: Session = Depends(get_db)):
    if not start_date:
        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=today.weekday()) # Monday of current week

    end_date = start_date + timedelta(days=6) # Sunday
    tasks = db.query(Task).filter(
        Task.scheduled_date >= start_date,
        Task.scheduled_date <= end_date
    ).all()

    days_map: Dict[str, List[Any]] = {}
    for i in range(7):
        d = start_date + timedelta(days=i)
        days_map[d.isoformat()] = []

    for t in tasks:
        d_str = t.scheduled_date.isoformat()
        if d_str in days_map:
            days_map[d_str].append(format_task_response(t))

    day_summaries = []
    for d_str, d_tasks in days_map.items():
        comp = sum(1 for t in d_tasks if t.status == "completed")
        day_summaries.append({
            "date": d_str,
            "day_name": datetime.strptime(d_str, "%Y-%m-%d").strftime("%A"),
            "total_tasks": len(d_tasks),
            "completed_tasks": comp,
            "tasks": d_tasks
        })

    return {
        "week_start": start_date.isoformat(),
        "week_end": end_date.isoformat(),
        "days": day_summaries
    }
