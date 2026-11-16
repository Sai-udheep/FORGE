def test_category_crud_api(client):
    # 1. Create
    resp = client.post("/api/v1/categories", json={
        "name": "Academics",
        "color": "#3B82F6",
        "icon": "book"
    })
    assert resp.status_code == 201
    cat_id = resp.json()["id"]
    assert resp.json()["name"] == "Academics"

    # 2. Duplicate name check
    dup_resp = client.post("/api/v1/categories", json={
        "name": "Academics",
        "color": "#3B82F6"
    })
    assert dup_resp.status_code == 400

    # 3. List
    list_resp = client.get("/api/v1/categories")
    assert list_resp.status_code == 200
    names = [c["name"] for c in list_resp.json()]
    assert "Academics" in names

    # 4. Patch
    patch_resp = client.patch(f"/api/v1/categories/{cat_id}", json={"color": "#1D4ED8"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["color"] == "#1D4ED8"

    # 5. Delete
    del_resp = client.delete(f"/api/v1/categories/{cat_id}")
    assert del_resp.status_code == 204

def test_goal_crud_api(client):
    # 1. Create
    resp = client.post("/api/v1/goals", json={
        "title": "InfoEdge Ready - Spring Boot & System Design",
        "priority": "high",
        "status": "active"
    })
    assert resp.status_code == 201
    goal_id = resp.json()["id"]

    # 2. Get
    get_resp = client.get(f"/api/v1/goals/{goal_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "InfoEdge Ready - Spring Boot & System Design"

    # 3. Patch
    patch_resp = client.patch(f"/api/v1/goals/{goal_id}", json={"progress_percentage": 45.0})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["progress_percentage"] == 45.0
