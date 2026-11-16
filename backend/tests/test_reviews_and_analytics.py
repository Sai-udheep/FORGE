from datetime import date

def test_daily_review_workflow(client):
    today = date.today().isoformat()
    # 1. Fetch review for today (auto-generates counts)
    get_resp = client.get(f"/api/v1/reviews/daily/{today}")
    assert get_resp.status_code == 200
    rev = get_resp.json()
    assert rev["review_date"] == today

    # 2. Save reflections
    save_resp = client.post("/api/v1/reviews/daily", json={
        "review_date": today,
        "accomplishments": "Completed 2 GATE topics and 1 SDE coding session.",
        "obstacles": "Context switching during afternoon.",
        "tomorrow_priorities": "Focus on OS Paging and Spring Data JPA.",
        "energy_rating": 4
    })
    assert save_resp.status_code == 200
    assert save_resp.json()["energy_rating"] == 4
    assert "Spring Data JPA" in save_resp.json()["tomorrow_priorities"]

def test_dashboard_analytics_api(client):
    resp = client.get("/api/v1/analytics/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "today_tasks_total" in data
    assert "today_completion_percentage" in data
    assert "streak" in data
    assert "weekly_velocity" in data
    assert len(data["weekly_velocity"]) == 7
