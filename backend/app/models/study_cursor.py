from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampedBase

class StudyCursorConnection(TimestampedBase):
    __tablename__ = "study_cursor_connections"
    
    name = Column(String(64), nullable=False, default="Local Study Cursor")
    workspace_path = Column(String(255), nullable=False)
    sync_mode = Column(String(32), default="manifest_and_cloud", nullable=False)
    supabase_url = Column(String(255), nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String(24), default="idle") # idle, syncing, success, error
    error_message = Column(Text, nullable=True)
    
    topic_references = relationship("StudyCursorTopicReference", back_populates="connection", cascade="all, delete-orphan")

class StudyCursorTopicReference(TimestampedBase):
    __tablename__ = "study_cursor_topic_references"
    
    connection_id = Column(String(36), ForeignKey("study_cursor_connections.id", ondelete="CASCADE"), nullable=False, index=True)
    track_category = Column(String(32), nullable=False, index=True) # gate, sde, ai, aptitude
    subject_key = Column(String(64), nullable=True, index=True)    # e.g. discreteMathematics, databases
    topic_id = Column(String(64), nullable=False, index=True)       # e.g. dm-1, sde-4, ai-12, apt-1
    topic_title = Column(String(255), nullable=False)
    cluster_name = Column(String(128), nullable=True)
    weightage = Column(String(64), nullable=True)
    subtopics_json = Column(Text, nullable=True)                    # JSON serialized list of subtopics
    status_in_study_cursor = Column(String(24), default="pending")  # pending, done
    last_verified_at = Column(DateTime, nullable=True)
    
    connection = relationship("StudyCursorConnection", back_populates="topic_references")
    tasks = relationship("Task", back_populates="study_cursor_topic_ref")
    focus_sessions = relationship("FocusSession", back_populates="study_cursor_topic_ref")
