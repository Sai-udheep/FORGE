import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.study_cursor import StudyCursorConnection, StudyCursorTopicReference
from app.models.task import Task
from app.models.sync import SyncMetadata
from app.schemas.study_cursor import (
    StudyCursorTopicImportRequest,
    StudyCursorCompletionConfirmRequest,
    StudyCursorStatusResponse,
    StudyCursorTopicResponse
)

logger = logging.getLogger(__name__)

class StudyCursorAdapter:
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or settings.STUDY_CURSOR_DIR
        self.manifest_path = self.workspace_path / "seed-data.json"
        self.env_path = self.workspace_path / ".env.local"
        self._supabase_url: Optional[str] = None
        self._supabase_anon_key: Optional[str] = None
        self._load_supabase_credentials()

    def _load_supabase_credentials(self):
        """Reads Supabase URL and key from Study Cursor's .env.local if present (Read-Only)."""
        if self.env_path.exists():
            try:
                with open(self.env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("VITE_SUPABASE_URL="):
                            url = line.split("=", 1)[1].strip().strip('"').strip("'")
                            self._supabase_url = url.rstrip("/")
                        elif line.startswith("VITE_SUPABASE_ANON_KEY="):
                            self._supabase_anon_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception as e:
                logger.warning(f"Could not read Study Cursor .env.local: {e}")

    def get_or_create_connection(self, db: Session) -> StudyCursorConnection:
        conn = db.query(StudyCursorConnection).first()
        if not conn:
            conn = StudyCursorConnection(
                name="Local Study Cursor",
                workspace_path=str(self.workspace_path),
                sync_mode="manifest_and_cloud" if self._supabase_url else "manifest_only",
                supabase_url=self._supabase_url,
                sync_status="idle"
            )
            db.add(conn)
            db.commit()
            db.refresh(conn)
        return conn

    def ingest_manifest(self, db: Session) -> Dict[str, Any]:
        """Ingests static curriculum data from Study Cursor's seed-data.json in read-only mode."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Study Cursor manifest not found at {self.manifest_path}")

        conn = self.get_or_create_connection(db)
        
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        ingested_count = 0

        # 1. GATE Tracks (11 Subjects across 5 Clusters)
        gate_subjects = data.get("gate", {})
        for subj_key, subj_data in gate_subjects.items():
            if not isinstance(subj_data, dict):
                continue
            cluster_name = subj_data.get("cluster")
            weightage = subj_data.get("weightage")
            for topic in subj_data.get("topics", []):
                self._upsert_topic_ref(
                    db,
                    conn.id,
                    track_category="gate",
                    subject_key=subj_key,
                    topic_id=topic["id"],
                    topic_title=topic["title"],
                    cluster_name=cluster_name,
                    weightage=weightage,
                    subtopics=topic.get("subtopics", []),
                    initial_status=topic.get("status", "pending")
                )
                ingested_count += 1

        # 2. General Aptitude (Continuous 15-Minute Track)
        aptitude = data.get("aptitude", {})
        if isinstance(aptitude, dict):
            for topic in aptitude.get("topics", []):
                self._upsert_topic_ref(
                    db,
                    conn.id,
                    track_category="aptitude",
                    subject_key="generalAptitude",
                    topic_id=topic["id"],
                    topic_title=topic["title"],
                    cluster_name="General Aptitude (Continuous 15-Min)",
                    weightage="Fixed 15 Marks",
                    subtopics=topic.get("subtopics", []),
                    initial_status=topic.get("status", "pending")
                )
                ingested_count += 1

        # 3. SDE Prep Track
        sde = data.get("sde", {})
        if isinstance(sde, dict):
            for topic in sde.get("topics", []):
                self._upsert_topic_ref(
                    db,
                    conn.id,
                    track_category="sde",
                    subject_key="sdePrep",
                    topic_id=topic["id"],
                    topic_title=topic["title"],
                    cluster_name="SDE Interview & Core CS Prep",
                    weightage=None,
                    subtopics=topic.get("subtopics", []),
                    initial_status=topic.get("status", "pending")
                )
                ingested_count += 1

        # 4. AI Engineering Track
        ai = data.get("ai", {})
        if isinstance(ai, dict):
            for topic in ai.get("topics", []):
                self._upsert_topic_ref(
                    db,
                    conn.id,
                    track_category="ai",
                    subject_key="aiEngineering",
                    topic_id=topic["id"],
                    topic_title=topic["title"],
                    cluster_name="AI Engineering Specialization",
                    weightage=None,
                    subtopics=topic.get("subtopics", []),
                    initial_status=topic.get("status", "pending")
                )
                ingested_count += 1

        conn.last_sync_at = datetime.now(timezone.utc)
        conn.sync_status = "success"
        db.commit()

        return {
            "success": True,
            "total_topics_ingested": ingested_count,
            "synced_at": conn.last_sync_at.isoformat()
        }

    def _upsert_topic_ref(
        self,
        db: Session,
        connection_id: str,
        track_category: str,
        subject_key: Optional[str],
        topic_id: str,
        topic_title: str,
        cluster_name: Optional[str],
        weightage: Optional[str],
        subtopics: List[str],
        initial_status: str
    ):
        existing = db.query(StudyCursorTopicReference).filter(
            StudyCursorTopicReference.connection_id == connection_id,
            StudyCursorTopicReference.topic_id == topic_id
        ).first()

        subtopics_str = json.dumps(subtopics)

        if existing:
            existing.topic_title = topic_title
            existing.cluster_name = cluster_name
            existing.weightage = weightage
            existing.subtopics_json = subtopics_str
            # Do NOT overwrite a completed status with pending
            if existing.status_in_study_cursor != "done":
                existing.status_in_study_cursor = initial_status
        else:
            new_ref = StudyCursorTopicReference(
                connection_id=connection_id,
                track_category=track_category,
                subject_key=subject_key,
                topic_id=topic_id,
                topic_title=topic_title,
                cluster_name=cluster_name,
                weightage=weightage,
                subtopics_json=subtopics_str,
                status_in_study_cursor=initial_status,
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(new_ref)

    def get_status(self, db: Session) -> StudyCursorStatusResponse:
        conn = self.get_or_create_connection(db)
        topics = db.query(StudyCursorTopicReference).filter(
            StudyCursorTopicReference.connection_id == conn.id
        ).all()

        total = len(topics)
        completed = sum(1 for t in topics if t.status_in_study_cursor == "done")
        pending = total - completed

        tracks_summary = {}
        for t in topics:
            tracks_summary[t.track_category] = tracks_summary.get(t.track_category, 0) + 1

        return StudyCursorStatusResponse(
            connection_id=conn.id,
            workspace_path=str(self.workspace_path),
            is_connected=self.workspace_path.exists(),
            sync_mode=conn.sync_mode,
            last_sync_at=conn.last_sync_at,
            sync_status=conn.sync_status,
            total_topics_tracked=total,
            completed_topics_count=completed,
            pending_topics_count=pending,
            tracks_summary=tracks_summary
        )

    def import_topic_to_planner(self, db: Session, req: StudyCursorTopicImportRequest) -> Task:
        conn = self.get_or_create_connection(db)
        topic_ref = db.query(StudyCursorTopicReference).filter(
            StudyCursorTopicReference.connection_id == conn.id,
            StudyCursorTopicReference.topic_id == req.topic_id
        ).first()

        if not topic_ref:
            raise ValueError(f"Topic {req.topic_id} not found in Study Cursor catalog.")

        # Determine realistic default duration: Aptitude is strictly 15 minutes!
        if req.estimated_duration_minutes:
            duration = req.estimated_duration_minutes
        elif topic_ref.track_category == "aptitude":
            duration = settings.APTITUDE_DAILY_MINUTES # 15 minutes
        else:
            duration = settings.POMODORO_DURATION_MINUTES # 50 minutes

        # Parse subtasks if available
        subtasks_list = []
        if topic_ref.subtopics_json:
            try:
                sub_strings = json.loads(topic_ref.subtopics_json)
                for idx, s in enumerate(sub_strings):
                    subtasks_list.append({"id": f"sub-{idx+1}", "title": s, "completed": False})
            except Exception:
                pass

        task = Task(
            title=f"[{topic_ref.track_category.upper()}] {topic_ref.topic_title}",
            description=f"Study Cursor Topic: {topic_ref.topic_title}\nCluster: {topic_ref.cluster_name or 'General'}\nMarks Weightage: {topic_ref.weightage or 'N/A'}",
            study_cursor_topic_ref_id=topic_ref.id,
            goal_id=req.goal_id,
            priority="high" if topic_ref.track_category == "gate" else "medium",
            estimated_duration_minutes=duration,
            scheduled_date=datetime.strptime(req.scheduled_date, "%Y-%m-%d").date() if req.scheduled_date else datetime.now(timezone.utc).date(),
            subtasks_json=json.dumps(subtasks_list) if subtasks_list else None
        )

        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def confirm_topic_completion(self, db: Session, req: StudyCursorCompletionConfirmRequest) -> Dict[str, Any]:
        """Marks topic complete only upon explicit user confirmation and logs synchronization metadata."""
        if not req.explicitly_confirmed_by_user:
            raise ValueError("Topic completion requires explicit user confirmation.")

        conn = self.get_or_create_connection(db)
        topic_ref = db.query(StudyCursorTopicReference).filter(
            StudyCursorTopicReference.connection_id == conn.id,
            StudyCursorTopicReference.topic_id == req.topic_id
        ).first()

        if not topic_ref:
            raise ValueError(f"Topic reference {req.topic_id} not found.")

        # 1. Update local topic reference
        topic_ref.status_in_study_cursor = "done"
        topic_ref.last_verified_at = datetime.now(timezone.utc)

        # 2. Update associated tasks in FORGE
        tasks = db.query(Task).filter(
            Task.study_cursor_topic_ref_id == topic_ref.id,
            Task.status != "completed"
        ).all()
        for t in tasks:
            t.status = "completed"
            t.completed_at = datetime.now(timezone.utc)
            t.actual_duration_minutes = max(t.actual_duration_minutes, req.actual_duration_minutes)

        # 3. Record Sync Metadata
        sync_meta = SyncMetadata(
            source_device="forge-backend",
            entity_type="study_cursor_sync",
            entity_id=topic_ref.id,
            operation="update",
            client_timestamp=datetime.now(timezone.utc),
            server_timestamp=datetime.now(timezone.utc),
            status="applied"
        )
        db.add(sync_meta)
        db.commit()

        # 4. Push to Supabase if configured
        cloud_pushed = False
        if self._supabase_url and self._supabase_anon_key:
            try:
                # Target endpoint: PostgREST upsert on tracker_data
                headers = {
                    "apikey": self._supabase_anon_key,
                    "Authorization": f"Bearer {self._supabase_anon_key}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                }
                # Study cursor stores by track key: e.g. track:gate:discreteMathematics
                track_key = f"track:{topic_ref.track_category}:{topic_ref.subject_key}" if topic_ref.subject_key else f"track:{topic_ref.track_category}"
                
                # Fetch existing track row first to preserve sibling topics
                with httpx.Client(timeout=5.0) as client:
                    resp = client.get(
                        f"{self._supabase_url}/rest/v1/tracker_data?id=eq.{track_key}&select=id,value",
                        headers=headers
                    )
                    if resp.status_code == 200 and resp.json():
                        row = resp.json()[0]
                        track_val = json.loads(row["value"])
                        # Mark the topic done in topics array
                        topics = track_val.get("topics", [])
                        for top in topics:
                            if top.get("id") == req.topic_id:
                                top["status"] = "done"
                                top["completedAt"] = datetime.now(timezone.utc).isoformat()
                        
                        # Upsert back
                        put_resp = client.post(
                            f"{self._supabase_url}/rest/v1/tracker_data",
                            headers=headers,
                            json={"id": track_key, "value": json.dumps(track_val), "updated_at": datetime.now(timezone.utc).isoformat()}
                        )
                        if put_resp.status_code in [200, 201]:
                            cloud_pushed = True
            except Exception as e:
                logger.warning(f"Failed to push cloud completion to Supabase: {e}")

        return {
            "success": True,
            "topic_id": req.topic_id,
            "status": "done",
            "cloud_pushed": cloud_pushed,
            "confirmed_at": datetime.now(timezone.utc).isoformat()
        }

adapter = StudyCursorAdapter()
