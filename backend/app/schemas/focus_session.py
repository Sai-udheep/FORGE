from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.study_cursor import StudyCursorTopicResponse

class FocusSessionStartRequest(BaseModel):
    task_id: Optional[str] = None
    study_cursor_topic_ref_id: Optional[str] = None
    session_type: str = "pomodoro" # pomodoro, flow, short_break, long_break
    planned_duration_minutes: int = 50
    notes: Optional[str] = None

class FocusSessionFinishRequest(BaseModel):
    actual_duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    confirm_topic_completed: Optional[bool] = False

class FocusSessionResponse(BaseModel):
    id: str
    task_id: Optional[str] = None
    study_cursor_topic_ref_id: Optional[str] = None
    session_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    planned_duration_minutes: int
    actual_duration_minutes: int
    status: str
    notes: Optional[str] = None
    created_at: datetime
    
    study_cursor_topic: Optional[StudyCursorTopicResponse] = None

    model_config = ConfigDict(from_attributes=True)
