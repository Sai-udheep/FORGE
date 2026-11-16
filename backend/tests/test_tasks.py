from datetime import date

def test_create_and_complete_task(client):
    payload = {
        "title": "Complete Discrete Maths Recurrences",
        "description": "Solve linear recurrences using characteristic roots",
        "priority": "high",
        "estimated_duration_minutes": 50,
        "scheduled_date": date.today().isoformat()
    }
    create_resp = client.post("/api/v1/tasks", json=payload)
    assert create_resp.status_code == 201
    task_data = create_resp.json()
    task_id = task_data["id"]
    assert task_data["title"] == payload["title"]
    assert task_data["status"] == "pending"

    # Mark complete
    complete_resp = client.post(f"/api/v1/tasks/{task_id}/complete", json={"actual_duration_minutes": 48})
    assert complete_resp.status_code == 200
    completed_data = complete_resp.json()
    assert completed_data["status"] == "completed"
    assert completed_data["actual_duration_minutes"] == 48
    assert completed_data["completed_at"] is not None

def test_reschedule_task(client):
    payload = {
        "title": "OS Paging Algorithms",
        "scheduled_date": "2026-11-20"
    }
    create_resp = client.post("/api/v1/tasks", json=payload)
    task_id = create_resp.json()["id"]

    reschedule_resp = client.post(f"/api/v1/tasks/{task_id}/reschedule", json={
        "new_date": "2026-11-22",
        "reason": "Prioritized GATE mock test"
    })
    assert reschedule_resp.status_code == 200
    assert reschedule_resp.json()["scheduled_date"] == "2026-11-22"
