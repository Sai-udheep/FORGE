from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampedBase

class FocusSession(TimestampedBase):
    __tablename__ = "focus_sessions"
    
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    study_cursor_topic_ref_id = Column(String(36), ForeignKey("study_cursor_topic_references.id", ondelete="SET NULL"), nullable=True, index=True)
    
    session_type = Column(String(24), default="pomodoro", nullable=False) # pomodoro, flow, short_break, long_break
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    planned_duration_minutes = Column(Integer, nullable=False, default=50)
    actual_duration_minutes = Column(Integer, nullable=False, default=0)
    status = Column(String(24), default="active", nullable=False) # active, paused, completed, abandoned
    notes = Column(Text, nullable=True)
    
    task = relationship("Task", back_populates="focus_sessions")
    study_cursor_topic_ref = relationship("StudyCursorTopicReference", back_populates="focus_sessions")
