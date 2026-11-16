from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ReminderBase(BaseModel):
    task_id: str
    reminder_time: datetime
    target_platform: str = "all" # all, kde, android

class ReminderCreate(ReminderBase):
    pass

class ReminderSnoozeRequest(BaseModel):
    snooze_minutes: int = 10

class ReminderResponse(ReminderBase):
    id: str
    status: str
    snooze_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
