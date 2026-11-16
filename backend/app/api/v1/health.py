from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Validates service health and SQLite connectivity."""
    db_healthy = False
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        pass

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/status", tags=["Health"])
def system_status(db: Session = Depends(get_db)):
    from app.models.task import Task
    from app.models.focus_session import FocusSession
    
    today = datetime.now(timezone.utc).date()
    today_tasks_count = db.query(Task).filter(Task.scheduled_date == today).count()
    completed_today = db.query(Task).filter(Task.scheduled_date == today, Task.status == "completed").count()
    active_focus = db.query(FocusSession).filter(FocusSession.status == "active").first()
    
    return {
        "today_tasks_total": today_tasks_count,
        "today_tasks_completed": completed_today,
        "has_active_focus_session": active_focus is not None,
        "active_focus_session_id": active_focus.id if active_focus else None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
