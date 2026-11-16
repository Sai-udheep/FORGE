from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class StudyCursorTopicResponse(BaseModel):
    id: str
    track_category: str
    subject_key: Optional[str] = None
    topic_id: str
    topic_title: str
    cluster_name: Optional[str] = None
    weightage: Optional[str] = None
    subtopics: List[str] = []
    status_in_study_cursor: str
    last_verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class StudyCursorStatusResponse(BaseModel):
    connection_id: Optional[str] = None
    workspace_path: str
    is_connected: bool
    sync_mode: str
    last_sync_at: Optional[datetime] = None
    sync_status: str
    total_topics_tracked: int
    completed_topics_count: int
    pending_topics_count: int
    tracks_summary: dict

class StudyCursorTopicImportRequest(BaseModel):
    topic_id: str
    scheduled_date: Optional[str] = None # YYYY-MM-DD
    scheduled_time: Optional[str] = None # HH:MM
    estimated_duration_minutes: Optional[int] = None
    goal_id: Optional[str] = None

class StudyCursorCompletionConfirmRequest(BaseModel):
    topic_id: str
    actual_duration_minutes: int
    notes: Optional[str] = None
    explicitly_confirmed_by_user: bool = True
