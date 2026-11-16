from datetime import date, datetime, timedelta, timezone

def test_planner_today_and_week(client):
    today = date.today().isoformat()
    # Create task for today
    client.post("/api/v1/tasks", json={
        "title": "Complete Algorithms MST Lecture",
        "scheduled_date": today,
        "estimated_duration_minutes": 50
    })

    # Test /planner/today
    today_resp = client.get("/api/v1/planner/today")
    assert today_resp.status_code == 200
    data = today_resp.json()
    assert data["metrics"]["total_tasks"] >= 1
    assert len(data["today_tasks"]) >= 1

    # Test /planner/week
    week_resp = client.get("/api/v1/planner/week")
    assert week_resp.status_code == 200
    week_data = week_resp.json()
    assert len(week_data["days"]) == 7

def test_reminders_snooze_and_dismiss(client):
    # 1. Create a task
    t_resp = client.post("/api/v1/tasks", json={
        "title": "Prepare GATE Mock Test",
        "scheduled_date": date.today().isoformat()
    })
    task_id = t_resp.json()["id"]

    # 2. Schedule reminder
    rem_time = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    rem_resp = client.post("/api/v1/reminders", json={
        "task_id": task_id,
        "reminder_time": rem_time
    })
    assert rem_resp.status_code == 201
    rem_id = rem_resp.json()["id"]

    # 3. Snooze reminder
    snooze_resp = client.post(f"/api/v1/reminders/{rem_id}/snooze", json={"snooze_minutes": 15})
    assert snooze_resp.status_code == 200
    assert snooze_resp.json()["status"] == "snoozed"
    assert snooze_resp.json()["snooze_count"] == 1

    # 4. Dismiss reminder
    dismiss_resp = client.post(f"/api/v1/reminders/{rem_id}/dismiss")
    assert dismiss_resp.status_code == 200
    assert dismiss_resp.json()["status"] == "dismissed"
