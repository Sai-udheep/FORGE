from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.intelligence.engine import ProductivityIntelligence

router = APIRouter(prefix="/intelligence", tags=["Productivity Intelligence"])

@router.get("/suggestions")
def get_daily_planning_suggestions(db: Session = Depends(get_db)):
    """Returns missed task alerts, workload balancing advice, and curriculum pacing rules."""
    return ProductivityIntelligence.get_planning_suggestions(db)

@router.get("/velocity")
def get_career_milestone_velocity(db: Session = Depends(get_db)):
    """Returns progress and velocity towards InfoEdge Internship and GATE 2027."""
    return ProductivityIntelligence.get_milestone_velocity(db)
