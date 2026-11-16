from sqlalchemy import Column, String, DateTime
from app.models.base import TimestampedBase

class SyncMetadata(TimestampedBase):
    __tablename__ = "sync_metadata"
    
    source_device = Column(String(64), nullable=False) # linux-plasmoid, android-phone, cli
    entity_type = Column(String(32), nullable=False, index=True) # task, focus_session, study_cursor_sync
    entity_id = Column(String(36), nullable=False, index=True)
    operation = Column(String(16), nullable=False) # create, update, delete
    client_timestamp = Column(DateTime, nullable=False)
    server_timestamp = Column(DateTime, nullable=False)
    status = Column(String(16), default="applied", nullable=False) # applied, conflict_resolved
