from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.category import CategoryResponse

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    target_date: Optional[date] = None
    priority: str = "medium" # low, medium, high, urgent
    status: str = "active"   # active, paused, completed, archived

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    target_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    progress_percentage: Optional[float] = None

class GoalResponse(GoalBase):
    id: str
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
