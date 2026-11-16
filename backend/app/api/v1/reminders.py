from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.reminder import Reminder
from app.models.task import Task
from app.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderSnoozeRequest
)

router = APIRouter(prefix="/reminders", tags=["Reminders"])

@router.get("", response_model=List[ReminderResponse])
def list_reminders(status_filter: str = "scheduled", db: Session = Depends(get_db)):
    query = db.query(Reminder)
    if status_filter:
        query = query.filter(Reminder.status == status_filter)
    return query.order_by(Reminder.reminder_time.asc()).all()

@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(payload: ReminderCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    reminder = Reminder(**payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@router.post("/{reminder_id}/snooze", response_model=ReminderResponse)
def snooze_reminder(reminder_id: str, payload: ReminderSnoozeRequest, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found.")
    
    reminder.status = "snoozed"
    reminder.snooze_count += 1
    reminder.reminder_time = datetime.now(timezone.utc) + timedelta(minutes=payload.snooze_minutes)
    
    db.commit()
    db.refresh(reminder)
    return reminder

@router.post("/{reminder_id}/dismiss", response_model=ReminderResponse)
def dismiss_reminder(reminder_id: str, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found.")
    
    reminder.status = "dismissed"
    db.commit()
    db.refresh(reminder)
    return reminder
