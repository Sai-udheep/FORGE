from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.models.base import TimestampedBase

class Category(TimestampedBase):
    __tablename__ = "categories"
    
    name = Column(String(64), unique=True, nullable=False, index=True)
    color = Column(String(16), nullable=False, default="#FF6B35") # Flame orange default
    icon = Column(String(32), default="folder")
    sort_order = Column(Integer, default=0)
    
    goals = relationship("Goal", back_populates="category", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="category")
