from sqlalchemy import Column, String, Text, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampedBase

class Goal(TimestampedBase):
    __tablename__ = "goals"
    
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    target_date = Column(Date, nullable=True)
    priority = Column(String(16), default="medium", nullable=False) # low, medium, high, urgent
    status = Column(String(20), default="active", nullable=False)   # active, paused, completed, archived
    progress_percentage = Column(Float, default=0.0)
    
    category = relationship("Category", back_populates="goals")
    tasks = relationship("Task", back_populates="goal")
