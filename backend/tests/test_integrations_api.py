from app.integrations.study_cursor_adapter import adapter

def test_study_cursor_api_integration(client, db):
    # 1. Trigger manifest sync via API
    sync_resp = client.post("/api/v1/integrations/study-cursor/sync")
    assert sync_resp.status_code == 200
    assert sync_resp.json()["total_topics_ingested"] >= 131

    # 2. Check status via API
    status_resp = client.get("/api/v1/integrations/study-cursor/status")
    assert status_resp.status_code == 200
    s_data = status_resp.json()
    assert s_data["is_connected"] is True
    assert s_data["total_topics_tracked"] >= 131

    # 3. List topics by track filter
    topics_resp = client.get("/api/v1/integrations/study-cursor/topics?track_category=gate")
    assert topics_resp.status_code == 200
    gate_topics = topics_resp.json()
    assert len(gate_topics) == 62 # Exact 62 GATE topics

    # 4. Import topic into planner
    import_resp = client.post("/api/v1/integrations/study-cursor/import-topic", json={
        "topic_id": "dm-1",
        "scheduled_date": "2026-11-17"
    })
    assert import_resp.status_code == 201
    task_data = import_resp.json()
    assert "[GATE]" in task_data["title"]
    assert task_data["study_cursor_topic"] is not None
    assert task_data["study_cursor_topic"]["topic_id"] == "dm-1"

    # 5. Confirm completion with explicit confirmation
    confirm_resp = client.post("/api/v1/integrations/study-cursor/confirm-completion", json={
        "topic_id": "dm-1",
        "actual_duration_minutes": 55,
        "explicitly_confirmed_by_user": True
    })
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "done"
