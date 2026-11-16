from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampedBase

class Reminder(TimestampedBase):
    __tablename__ = "reminders"
    
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    reminder_time = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), default="scheduled", nullable=False) # scheduled, triggered, snoozed, dismissed
    snooze_count = Column(Integer, default=0)
    target_platform = Column(String(24), default="all", nullable=False) # all, kde, android
    
    task = relationship("Task", back_populates="reminders")
