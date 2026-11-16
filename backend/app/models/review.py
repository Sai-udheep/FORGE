from sqlalchemy import Column, String, Text, Integer, Float, Date
from app.models.base import TimestampedBase

class DailyReview(TimestampedBase):
    __tablename__ = "daily_reviews"
    
    review_date = Column(Date, unique=True, nullable=False, index=True)
    planned_tasks_count = Column(Integer, default=0, nullable=False)
    completed_tasks_count = Column(Integer, default=0, nullable=False)
    focus_minutes_total = Column(Integer, default=0, nullable=False)
    accomplishments = Column(Text, nullable=True)
    obstacles = Column(Text, nullable=True)
    tomorrow_priorities = Column(Text, nullable=True)
    energy_rating = Column(Integer, nullable=True) # 1 to 5

class WeeklyReview(TimestampedBase):
    __tablename__ = "weekly_reviews"
    
    week_start_date = Column(Date, nullable=False, index=True)
    week_end_date = Column(Date, nullable=False)
    total_tasks_completed = Column(Integer, default=0, nullable=False)
    total_focus_hours = Column(Float, default=0.0, nullable=False)
    consistency_score = Column(Float, default=0.0) # 0 to 100 percentage
    weak_areas = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
