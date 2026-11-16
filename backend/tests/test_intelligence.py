from datetime import date, timedelta
from app.integrations.study_cursor_adapter import adapter

def test_intelligence_planning_suggestions(client, db):
    # 1. Create an overdue task
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    client.post("/api/v1/tasks", json={
        "title": "Unfinished Graph Algorithms",
        "scheduled_date": yesterday,
        "estimated_duration_minutes": 50
    })

    # 2. Ingest Study Cursor catalog
    adapter.ingest_manifest(db)

    # 3. Call intelligence suggestions
    resp = client.get("/api/v1/intelligence/suggestions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overdue_tasks_count"] >= 1
    
    types = [s["type"] for s in data["suggestions"]]
    assert "missed_task" in types
    assert "aptitude_reminder" in types # Aptitude reminder triggered if not scheduled

def test_career_milestone_velocity(client, db):
    adapter.ingest_manifest(db)
    resp = client.get("/api/v1/intelligence/velocity")
    assert resp.status_code == 200
    m = resp.json()["milestones"]
    assert "infoedge_sde_internship" in m
    assert "gate_2027" in m
    assert m["gate_2027"]["gate_mastery"]["total"] == 62
