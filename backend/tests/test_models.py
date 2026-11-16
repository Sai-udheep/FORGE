import uuid
from datetime import datetime, timezone
from app.models import Category, Goal, Task, FocusSession

def test_category_and_goal_models(db):
    cat = Category(name="Test Category", color="#FF5722")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    
    assert cat.id is not None
    assert cat.name == "Test Category"
    assert cat.created_at is not None

    goal = Goal(title="Master Spring Boot", category_id=cat.id, priority="high")
    db.add(goal)
    db.commit()
    db.refresh(goal)

    assert goal.id is not None
    assert goal.category.name == "Test Category"
    assert goal.priority == "high"

def test_task_creation(db):
    task = Task(title="Practice Graph Traversals", priority="high", estimated_duration_minutes=60)
    db.add(task)
    db.commit()
    db.refresh(task)

    assert task.id is not None
    assert task.status == "pending"
    assert task.actual_duration_minutes == 0
