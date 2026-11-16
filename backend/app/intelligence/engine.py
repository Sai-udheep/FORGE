from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.focus_session import FocusSession
from app.models.study_cursor import StudyCursorTopicReference

class ProductivityIntelligence:
    @staticmethod
    def get_planning_suggestions(db: Session) -> Dict[str, Any]:
        """Generates realistic workload suggestions, detects missed tasks, and checks track rules."""
        today = datetime.now(timezone.utc).date()
        weekday_name = datetime.now(timezone.utc).strftime("%A").lower()

        suggestions: List[Dict[str, Any]] = []

        # 1. Detect Missed / Overdue Tasks
        overdue_tasks = db.query(Task).filter(
            Task.scheduled_date < today,
            Task.status.in_(["pending", "in_progress"])
        ).all()

        for t in overdue_tasks:
            suggestions.append({
                "type": "missed_task",
                "severity": "warning",
                "task_id": t.id,
                "title": t.title,
                "message": f"Missed task: '{t.title}' was scheduled for {t.scheduled_date}. Consider rescheduling to today or back-burnering.",
                "action": "reschedule"
            })

        # 2. Workload & Cognitive Load Assessment for Today
        today_tasks = db.query(Task).filter(Task.scheduled_date == today).all()
        total_planned_minutes = sum(t.estimated_duration_minutes for t in today_tasks)
        gate_topics_today = [t for t in today_tasks if "[GATE]" in t.title or (t.study_cursor_topic_ref and t.study_cursor_topic_ref.track_category == "gate")]

        if total_planned_minutes > 240:
            suggestions.append({
                "type": "workload_overload",
                "severity": "high",
                "message": f"High cognitive load detected ({total_planned_minutes} mins / {round(total_planned_minutes/60, 1)} hrs). To maintain retention and avoid burnout, consider capping deep work at 4 hours.",
                "action": "balance_workload"
            })

        if len(gate_topics_today) > 2:
            suggestions.append({
                "type": "gate_pacing",
                "severity": "info",
                "message": f"You have {len(gate_topics_today)} GATE topics scheduled today. The 5-Cluster Mastery Engine recommends deep mastery of 1–2 topics per day.",
                "action": "pace_gate"
            })

        # 3. Aptitude Daily 15-Minute Compliance Check
        has_aptitude_today = any(
            "[APTITUDE]" in t.title or (t.study_cursor_topic_ref and t.study_cursor_topic_ref.track_category == "aptitude")
            for t in today_tasks
        )
        if not has_aptitude_today:
            suggestions.append({
                "type": "aptitude_reminder",
                "severity": "info",
                "message": "Continuous 15-Minute Daily Aptitude practice is not yet scheduled for today.",
                "action": "schedule_aptitude"
            })

        # 4. Weekly Rules Pacing (e.g. Wednesday SDE Dedication)
        if weekday_name == "wednesday":
            has_sde_today = any(
                "[SDE]" in t.title or (t.study_cursor_topic_ref and t.study_cursor_topic_ref.track_category == "sde")
                for t in today_tasks
            )
            if not has_sde_today:
                suggestions.append({
                    "type": "sde_day_reminder",
                    "severity": "info",
                    "message": "Today is Wednesday — dedicated SDE interview prep day in Study Cursor rules.",
                    "action": "schedule_sde"
                })

        return {
            "date": today.isoformat(),
            "total_planned_minutes": total_planned_minutes,
            "tasks_scheduled_today": len(today_tasks),
            "overdue_tasks_count": len(overdue_tasks),
            "suggestions": suggestions
        }

    @staticmethod
    def get_milestone_velocity(db: Session) -> Dict[str, Any]:
        """Calculates pace and velocity towards GATE 2027 and InfoEdge Internship (Jan 2027)."""
        topics = db.query(StudyCursorTopicReference).all()
        
        gate_topics = [t for t in topics if t.track_category == "gate"]
        sde_topics = [t for t in topics if t.track_category == "sde"]
        ai_topics = [t for t in topics if t.track_category == "ai"]
        apt_topics = [t for t in topics if t.track_category == "aptitude"]

        def calc_track(track_list):
            total = len(track_list)
            done = sum(1 for t in track_list if t.status_in_study_cursor == "done")
            pct = round((done / total * 100), 1) if total > 0 else 0.0
            return {"total": total, "completed": done, "percentage": pct}

        return {
            "milestones": {
                "infoedge_sde_internship": {
                    "target": "January 2027",
                    "priority": 1,
                    "focus": "Java, Spring Boot, SQL, Systems, Testing, Debugging",
                    "sde_prep": calc_track(sde_topics)
                },
                "gate_2027": {
                    "target": "February 2027",
                    "priority": 1,
                    "focus": "5-Cluster CS Mastery & General Aptitude",
                    "gate_mastery": calc_track(gate_topics),
                    "aptitude": calc_track(apt_topics)
                },
                "ai_engineering": {
                    "target": "Continuous Nightly Specialization",
                    "priority": 2,
                    "ai_roadmap": calc_track(ai_topics)
                }
            }
        }
