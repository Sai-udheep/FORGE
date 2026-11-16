import json
from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.models.study_cursor import StudyCursorTopicReference
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskCompleteRequest,
    TaskRescheduleRequest
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def format_task_response(t: Task) -> TaskResponse:
    subtasks = None
    if t.subtasks_json:
        try:
            subtasks = json.loads(t.subtasks_json)
        except Exception:
            pass

    sc_topic = None
    if t.study_cursor_topic_ref:
        ref: StudyCursorTopicReference = t.study_cursor_topic_ref
        st_list = []
        if ref.subtopics_json:
            try:
                st_list = json.loads(ref.subtopics_json)
            except Exception:
                pass
        sc_topic = {
            "id": ref.id,
            "track_category": ref.track_category,
            "subject_key": ref.subject_key,
            "topic_id": ref.topic_id,
            "topic_title": ref.topic_title,
            "cluster_name": ref.cluster_name,
            "weightage": ref.weightage,
            "subtopics": st_list,
            "status_in_study_cursor": ref.status_in_study_cursor,
            "last_verified_at": ref.last_verified_at
        }

    return TaskResponse(
        id=t.id,
        title=t.title,
        description=t.description,
        goal_id=t.goal_id,
        category_id=t.category_id,
        study_cursor_topic_ref_id=t.study_cursor_topic_ref_id,
        priority=t.priority,
        status=t.status,
        scheduled_date=t.scheduled_date,
        scheduled_time=t.scheduled_time,
        estimated_duration_minutes=t.estimated_duration_minutes,
        actual_duration_minutes=t.actual_duration_minutes,
        is_recurring=t.is_recurring,
        recurrence_rule=t.recurrence_rule,
        subtasks=subtasks,
        completed_at=t.completed_at,
        created_at=t.created_at,
        updated_at=t.updated_at,
        study_cursor_topic=sc_topic,
        category=t.category
    )

@router.get("", response_model=List[TaskResponse])
def list_tasks(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    goal_id: Optional[str] = None,
    category_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if date_from:
        query = query.filter(Task.scheduled_date >= date_from)
    if date_to:
        query = query.filter(Task.scheduled_date <= date_to)
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority:
        query = query.filter(Task.priority == priority)
    if goal_id:
        query = query.filter(Task.goal_id == goal_id)
    if category_id:
        query = query.filter(Task.category_id == category_id)

    tasks = query.order_by(Task.scheduled_date.asc(), Task.scheduled_time.asc()).all()
    return [format_task_response(t) for t in tasks]

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    subtasks = data.pop("subtasks", None)
    subtasks_json = json.dumps([s for s in subtasks]) if subtasks else None

    task = Task(**data, subtasks_json=subtasks_json)
    db.add(task)
    db.commit()
    db.refresh(task)
    return format_task_response(task)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return format_task_response(task)

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    data = payload.model_dump(exclude_unset=True)
    if "subtasks" in data:
        subtasks = data.pop("subtasks")
        task.subtasks_json = json.dumps([s for s in subtasks]) if subtasks is not None else None

    for k, v in data.items():
        setattr(task, k, v)
    
    db.commit()
    db.refresh(task)
    return format_task_response(task)

@router.post("/{task_id}/complete", response_model=TaskResponse)
def mark_task_complete(task_id: str, payload: TaskCompleteRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)
    if payload.actual_duration_minutes is not None:
        task.actual_duration_minutes = payload.actual_duration_minutes
    elif task.actual_duration_minutes == 0:
        task.actual_duration_minutes = task.estimated_duration_minutes

    db.commit()
    db.refresh(task)
    return format_task_response(task)

@router.post("/{task_id}/reschedule", response_model=TaskResponse)
def reschedule_task(task_id: str, payload: TaskRescheduleRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    task.scheduled_date = payload.new_date
    if payload.new_time is not None:
        task.scheduled_time = payload.new_time
    
    db.commit()
    db.refresh(task)
    return format_task_response(task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(task)
    db.commit()
    return None
