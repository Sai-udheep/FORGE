from app.integrations.study_cursor_adapter import StudyCursorAdapter
from app.schemas.study_cursor import (
    StudyCursorTopicImportRequest,
    StudyCursorCompletionConfirmRequest
)

def test_manifest_ingestion(db):
    adapter = StudyCursorAdapter()
    result = adapter.ingest_manifest(db)
    assert result["success"] is True
    assert result["total_topics_ingested"] >= 131 # At least 62 GATE + 10 Aptitude + 20+ SDE + 39 AI

    status = adapter.get_status(db)
    assert status.is_connected is True
    assert status.total_topics_tracked >= 131
    assert "gate" in status.tracks_summary
    assert "aptitude" in status.tracks_summary
    assert "sde" in status.tracks_summary
    assert "ai" in status.tracks_summary

def test_aptitude_15_minute_enforcement(db):
    adapter = StudyCursorAdapter()
    adapter.ingest_manifest(db)

    # Import an aptitude topic
    req = StudyCursorTopicImportRequest(topic_id="apt-1")
    task = adapter.import_topic_to_planner(db, req)

    # Must be strictly 15 minutes by default!
    assert task.estimated_duration_minutes == 15
    assert "APTITUDE" in task.title

def test_explicit_confirmation_required_for_completion(db):
    adapter = StudyCursorAdapter()
    adapter.ingest_manifest(db)

    # Without explicit confirmation, ValueError must be raised
    req_unconfirmed = StudyCursorCompletionConfirmRequest(
        topic_id="dm-1",
        actual_duration_minutes=50,
        explicitly_confirmed_by_user=False
    )
    try:
        adapter.confirm_topic_completion(db, req_unconfirmed)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "explicit user confirmation" in str(e)

    # With explicit confirmation, succeeds
    req_confirmed = StudyCursorCompletionConfirmRequest(
        topic_id="dm-1",
        actual_duration_minutes=50,
        explicitly_confirmed_by_user=True
    )
    result = adapter.confirm_topic_completion(db, req_confirmed)
    assert result["success"] is True
    assert result["status"] == "done"
