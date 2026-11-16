import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.integrations.study_cursor_adapter import adapter
from app.models.study_cursor import StudyCursorTopicReference
from app.schemas.study_cursor import (
    StudyCursorStatusResponse,
    StudyCursorTopicResponse,
    StudyCursorTopicImportRequest,
    StudyCursorCompletionConfirmRequest
)
from app.schemas.task import TaskResponse
from app.api.v1.tasks import format_task_response

router = APIRouter(prefix="/integrations/study-cursor", tags=["Study Cursor Integration"])

@router.get("/status", response_model=StudyCursorStatusResponse)
def get_study_cursor_status(db: Session = Depends(get_db)):
    """Returns current connectivity, last sync time, and topic counts for Study Cursor."""
    return adapter.get_status(db)

@router.post("/sync")
def trigger_manifest_sync(db: Session = Depends(get_db)):
    """Triggers a read-only ingestion/sync of Study Cursor catalog from seed-data.json."""
    try:
        return adapter.ingest_manifest(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/topics", response_model=List[StudyCursorTopicResponse])
def list_topics(
    track_category: Optional[str] = None,
    subject_key: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists imported Study Cursor topics with optional filtering by track or status."""
    query = db.query(StudyCursorTopicReference)
    if track_category:
        query = query.filter(StudyCursorTopicReference.track_category == track_category)
    if subject_key:
        query = query.filter(StudyCursorTopicReference.subject_key == subject_key)
    if status_filter:
        query = query.filter(StudyCursorTopicReference.status_in_study_cursor == status_filter)

    topics = query.order_by(StudyCursorTopicReference.track_category.asc(), StudyCursorTopicReference.id.asc()).all()

    res = []
    for t in topics:
        st_list = []
        if t.subtopics_json:
            try:
                st_list = json.loads(t.subtopics_json)
            except Exception:
                pass
        res.append(StudyCursorTopicResponse(
            id=t.id,
            track_category=t.track_category,
            subject_key=t.subject_key,
            topic_id=t.topic_id,
            topic_title=t.topic_title,
            cluster_name=t.cluster_name,
            weightage=t.weightage,
            subtopics=st_list,
            status_in_study_cursor=t.status_in_study_cursor,
            last_verified_at=t.last_verified_at
        ))
    return res

@router.post("/import-topic", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def import_topic_to_planner(payload: StudyCursorTopicImportRequest, db: Session = Depends(get_db)):
    """Imports an eligible Study Cursor topic into the FORGE daily planner as a Task."""
    try:
        task = adapter.import_topic_to_planner(db, payload)
        return format_task_response(task)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import topic: {str(e)}")

@router.post("/confirm-completion")
def confirm_topic_completion(payload: StudyCursorCompletionConfirmRequest, db: Session = Depends(get_db)):
    """
    Explicit user confirmation gate: marks topic complete in FORGE and pushes status to Study Cursor.
    Never marks a topic complete automatically when a focus timer finishes.
    """
    if not payload.explicitly_confirmed_by_user:
        raise HTTPException(
            status_code=400,
            detail="Explicit user confirmation is strictly required to mark a Study Cursor topic complete."
        )
    try:
        return adapter.confirm_topic_completion(db, payload)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm completion: {str(e)}")
