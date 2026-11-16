from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DailyReviewBase(BaseModel):
    review_date: date
    accomplishments: Optional[str] = None
    obstacles: Optional[str] = None
    tomorrow_priorities: Optional[str] = None
    energy_rating: Optional[int] = 5 # 1 to 5

class DailyReviewCreate(DailyReviewBase):
    pass

class DailyReviewResponse(DailyReviewBase):
    id: str
    planned_tasks_count: int
    completed_tasks_count: int
    focus_minutes_total: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WeeklyReviewBase(BaseModel):
    week_start_date: date
    week_end_date: date
    weak_areas: Optional[str] = None
    recommendations: Optional[str] = None

class WeeklyReviewCreate(WeeklyReviewBase):
    pass

class WeeklyReviewResponse(WeeklyReviewBase):
    id: str
    total_tasks_completed: int
    total_focus_hours: float
    consistency_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
