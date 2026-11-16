from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.focus_session import FocusSession
from app.models.task import Task
from app.schemas.focus_session import (
    FocusSessionStartRequest,
    FocusSessionFinishRequest,
    FocusSessionResponse
)

router = APIRouter(prefix="/focus", tags=["Focus Sessions"])

@router.get("/active", response_model=Optional[FocusSessionResponse])
def get_active_session(db: Session = Depends(get_db)):
    session = db.query(FocusSession).filter(FocusSession.status == "active").first()
    return session

@router.get("/history", response_model=List[FocusSessionResponse])
def get_session_history(limit: int = 20, db: Session = Depends(get_db)):
    return db.query(FocusSession).order_by(FocusSession.created_at.desc()).limit(limit).all()

@router.post("/start", response_model=FocusSessionResponse, status_code=status.HTTP_201_CREATED)
def start_focus_session(payload: FocusSessionStartRequest, db: Session = Depends(get_db)):
    # Pause or complete any existing active session
    active = db.query(FocusSession).filter(FocusSession.status == "active").first()
    if active:
        now = datetime.now(timezone.utc)
        active.status = "paused"
        duration_so_far = int((now - active.start_time.replace(tzinfo=timezone.utc)).total_seconds() / 60)
        active.actual_duration_minutes += max(0, duration_so_far)

    session = FocusSession(
        task_id=payload.task_id,
        study_cursor_topic_ref_id=payload.study_cursor_topic_ref_id,
        session_type=payload.session_type,
        start_time=datetime.now(timezone.utc),
        planned_duration_minutes=payload.planned_duration_minutes,
        status="active",
        notes=payload.notes
    )
    db.add(session)

    # If linked to a task, set task status to in_progress
    if payload.task_id:
        task = db.query(Task).filter(Task.id == payload.task_id).first()
        if task and task.status == "pending":
            task.status = "in_progress"

    db.commit()
    db.refresh(session)
    return session

@router.post("/{session_id}/pause", response_model=FocusSessionResponse)
def pause_focus_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Focus session not found.")
    
    if session.status == "active":
        now = datetime.now(timezone.utc)
        elapsed = int((now - session.start_time.replace(tzinfo=timezone.utc)).total_seconds() / 60)
        session.actual_duration_minutes += max(0, elapsed)
        session.status = "paused"
        db.commit()
        db.refresh(session)
    return session

@router.post("/{session_id}/resume", response_model=FocusSessionResponse)
def resume_focus_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Focus session not found.")
    
    session.status = "active"
    session.start_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session

@router.post("/{session_id}/finish", response_model=FocusSessionResponse)
def finish_focus_session(session_id: str, payload: FocusSessionFinishRequest, db: Session = Depends(get_db)):
    session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Focus session not found.")
    
    now = datetime.now(timezone.utc)
    session.end_time = now
    session.status = "completed"

    if payload.actual_duration_minutes is not None:
        session.actual_duration_minutes = payload.actual_duration_minutes
    elif session.status == "active":
        elapsed = int((now - session.start_time.replace(tzinfo=timezone.utc)).total_seconds() / 60)
        session.actual_duration_minutes += max(0, elapsed)

    if payload.notes:
        session.notes = (session.notes or "") + f"\n{payload.notes}"

    # Log duration onto the task
    if session.task_id:
        task = db.query(Task).filter(Task.id == session.task_id).first()
        if task:
            task.actual_duration_minutes += session.actual_duration_minutes

    db.commit()
    db.refresh(session)
    return session
