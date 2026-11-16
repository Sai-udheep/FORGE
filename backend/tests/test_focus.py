def test_focus_session_lifecycle(client):
    # 1. Start session
    start_resp = client.post("/api/v1/focus/start", json={
        "session_type": "pomodoro",
        "planned_duration_minutes": 50,
        "notes": "Deep focus on SQL indexing"
    })
    assert start_resp.status_code == 201
    session_data = start_resp.json()
    session_id = session_data["id"]
    assert session_data["status"] == "active"

    # 2. Verify active session endpoint
    active_resp = client.get("/api/v1/focus/active")
    assert active_resp.status_code == 200
    assert active_resp.json()["id"] == session_id

    # 3. Pause session
    pause_resp = client.post(f"/api/v1/focus/{session_id}/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    # 4. Resume session
    resume_resp = client.post(f"/api/v1/focus/{session_id}/resume")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "active"

    # 5. Finish session
    finish_resp = client.post(f"/api/v1/focus/{session_id}/finish", json={
        "actual_duration_minutes": 52,
        "notes": "Completed exercises cleanly."
    })
    assert finish_resp.status_code == 200
    assert finish_resp.json()["status"] == "completed"
    assert finish_resp.json()["actual_duration_minutes"] == 52
