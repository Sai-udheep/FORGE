from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.study_cursor import StudyCursorTopicResponse
from app.schemas.category import CategoryResponse

class SubTaskItem(BaseModel):
    id: str
    title: str
    completed: bool = False

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    goal_id: Optional[str] = None
    category_id: Optional[str] = None
    study_cursor_topic_ref_id: Optional[str] = None
    priority: str = "medium" # low, medium, high, urgent
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    estimated_duration_minutes: int = 45
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    subtasks: Optional[List[SubTaskItem]] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goal_id: Optional[str] = None
    category_id: Optional[str] = None
    study_cursor_topic_ref_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    estimated_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    subtasks: Optional[List[SubTaskItem]] = None

class TaskCompleteRequest(BaseModel):
    actual_duration_minutes: Optional[int] = None
    notes: Optional[str] = None

class TaskRescheduleRequest(BaseModel):
    new_date: date
    new_time: Optional[time] = None
    reason: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    goal_id: Optional[str] = None
    category_id: Optional[str] = None
    study_cursor_topic_ref_id: Optional[str] = None
    priority: str
    status: str
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    estimated_duration_minutes: int
    actual_duration_minutes: int
    is_recurring: bool
    recurrence_rule: Optional[str] = None
    subtasks: Optional[List[Dict[str, Any]]] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    study_cursor_topic: Optional[StudyCursorTopicResponse] = None
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
