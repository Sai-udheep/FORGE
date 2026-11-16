from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.review import DailyReview, WeeklyReview
from app.models.task import Task
from app.models.focus_session import FocusSession
from app.schemas.review import (
    DailyReviewCreate,
    DailyReviewResponse,
    WeeklyReviewCreate,
    WeeklyReviewResponse
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.get("/daily/{review_date}", response_model=DailyReviewResponse)
def get_daily_review(review_date: date, db: Session = Depends(get_db)):
    review = db.query(DailyReview).filter(DailyReview.review_date == review_date).first()
    if not review:
        # Pre-populate counts for a new review on that date
        planned = db.query(Task).filter(Task.scheduled_date == review_date).count()
        completed = db.query(Task).filter(Task.scheduled_date == review_date, Task.status == "completed").count()
        sessions = db.query(FocusSession).filter(FocusSession.created_at >= datetime.combine(review_date, datetime.min.time())).all()
        focus_mins = sum(s.actual_duration_minutes for s in sessions)
        
        review = DailyReview(
            review_date=review_date,
            planned_tasks_count=planned,
            completed_tasks_count=completed,
            focus_minutes_total=focus_mins,
            energy_rating=5
        )
        db.add(review)
        db.commit()
        db.refresh(review)
    return review

@router.post("/daily", response_model=DailyReviewResponse)
def save_daily_review(payload: DailyReviewCreate, db: Session = Depends(get_db)):
    review = db.query(DailyReview).filter(DailyReview.review_date == payload.review_date).first()
    if not review:
        planned = db.query(Task).filter(Task.scheduled_date == payload.review_date).count()
        completed = db.query(Task).filter(Task.scheduled_date == payload.review_date, Task.status == "completed").count()
        sessions = db.query(FocusSession).filter(FocusSession.created_at >= datetime.combine(payload.review_date, datetime.min.time())).all()
        focus_mins = sum(s.actual_duration_minutes for s in sessions)
        
        review = DailyReview(
            review_date=payload.review_date,
            planned_tasks_count=planned,
            completed_tasks_count=completed,
            focus_minutes_total=focus_mins,
            **payload.model_dump(exclude={"review_date"})
        )
        db.add(review)
    else:
        for k, v in payload.model_dump().items():
            setattr(review, k, v)

    db.commit()
    db.refresh(review)
    return review

@router.get("/weekly/{start_date}", response_model=WeeklyReviewResponse)
def get_weekly_review(start_date: date, db: Session = Depends(get_db)):
    review = db.query(WeeklyReview).filter(WeeklyReview.week_start_date == start_date).first()
    if not review:
        end_date = start_date + timedelta(days=6)
        tasks = db.query(Task).filter(Task.scheduled_date >= start_date, Task.scheduled_date <= end_date).all()
        completed_count = sum(1 for t in tasks if t.status == "completed")
        total_count = len(tasks)
        score = (completed_count / total_count * 100.0) if total_count > 0 else 0.0

        focus_sessions = db.query(FocusSession).filter(
            FocusSession.start_time >= datetime.combine(start_date, datetime.min.time()),
            FocusSession.start_time <= datetime.combine(end_date, datetime.max.time())
        ).all()
        focus_hrs = round(sum(s.actual_duration_minutes for s in focus_sessions) / 60.0, 1)

        review = WeeklyReview(
            week_start_date=start_date,
            week_end_date=end_date,
            total_tasks_completed=completed_count,
            total_focus_hours=focus_hrs,
            consistency_score=round(score, 1)
        )
        db.add(review)
        db.commit()
        db.refresh(review)
    return review

@router.post("/weekly", response_model=WeeklyReviewResponse)
def save_weekly_review(payload: WeeklyReviewCreate, db: Session = Depends(get_db)):
    review = db.query(WeeklyReview).filter(WeeklyReview.week_start_date == payload.week_start_date).first()
    if not review:
        review = WeeklyReview(**payload.model_dump())
        db.add(review)
    else:
        for k, v in payload.model_dump().items():
            setattr(review, k, v)
    db.commit()
    db.refresh(review)
    return review
