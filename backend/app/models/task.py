from sqlalchemy import Column, String, Text, Date, Time, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampedBase

class Task(TimestampedBase):
    __tablename__ = "tasks"
    
    goal_id = Column(String(36), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    study_cursor_topic_ref_id = Column(String(36), ForeignKey("study_cursor_topic_references.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(16), default="medium", nullable=False) # low, medium, high, urgent
    status = Column(String(24), default="pending", nullable=False, index=True) # pending, in_progress, completed, cancelled
    
    scheduled_date = Column(Date, nullable=True, index=True)
    scheduled_time = Column(Time, nullable=True)
    estimated_duration_minutes = Column(Integer, default=45, nullable=False)
    actual_duration_minutes = Column(Integer, default=0, nullable=False)
    
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(64), nullable=True)
    subtasks_json = Column(Text, nullable=True) # JSON array of {id, title, completed}
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    goal = relationship("Goal", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    study_cursor_topic_ref = relationship("StudyCursorTopicReference", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")
    focus_sessions = relationship("FocusSession", back_populates="task")
